# app/services/recommendation_service.py
# Modular rule-based recommendation engine for Noor's Attire.
# Easily replaceable with an AI/ML recommendation service in the future.

from typing import List, Dict, Any
from app.services.firebase_service import get_all, get_one

def get_complete_the_look(product_id: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Returns complementary products to complete an attire look.
    Uses admin-configured 'complete_the_look_ids' first, falling back to
    cross-category pairings (e.g. Pashtun Dress -> Shawl / Accessory).
    """
    target = get_one("products", product_id)
    all_products = get_all("products")
    if not target:
        return [p for p in all_products if p.get("id") != product_id][:limit]

    configured_ids = target.get("complete_the_look_ids", [])
    recommendations = []

    # 1. First add admin-configured bundle items
    if configured_ids:
        for p in all_products:
            if p.get("id") in configured_ids and p.get("id") != product_id:
                p["recommendation_reason"] = "Styled by Noor's master designer"
                recommendations.append(p)

    # 2. If fewer than limit, add complementary category items
    if len(recommendations) < limit:
        target_cat = target.get("category", "")
        for p in all_products:
            p_id = p.get("id")
            if p_id == product_id or any(r.get("id") == p_id for r in recommendations):
                continue
            # Complementary category logic
            p_cat = p.get("category", "")
            if target_cat == "pashtun_dresses" and p_cat in ["shawls", "accessories", "paint_shirts"]:
                p["recommendation_reason"] = "Matching royal accessory"
                recommendations.append(p)
            elif target_cat == "paint_shirts" and p_cat in ["shawls", "pashtun_dresses"]:
                p["recommendation_reason"] = "Artisan pairing"
                recommendations.append(p)
            
            if len(recommendations) >= limit:
                break

    # 3. Fallback to generic other products if still below limit
    if len(recommendations) < limit:
        for p in all_products:
            p_id = p.get("id")
            if p_id != product_id and not any(r.get("id") == p_id for r in recommendations):
                p["recommendation_reason"] = "Popular companion piece"
                recommendations.append(p)
                if len(recommendations) >= limit:
                    break

    return recommendations[:limit]


def get_smart_recommendations(product_id: str, limit: int = 6) -> List[Dict[str, Any]]:
    """
    Rule-based recommendations based on category, related accessory clusters, price, and tag matching.
    Priority:
    1. Same category
    2. Similar product type / cluster
    3. Same collection / featured status
    4. Other relevant products
    """
    target = get_one("products", product_id)
    all_products = get_all("products")
    if not target:
        return [p for p in all_products if p.get("id") != product_id][:limit]

    target_category = (target.get("category") or "").lower().strip()
    target_price = float(target.get("price", 0))
    target_tags = set(t.lower() for t in target.get("tags", []))

    # Related cluster mapping
    clusters = {
        "watches": {"accessories", "keychains", "wallets"},
        "watch": {"accessories", "keychains", "wallets"},
        "perfumes": {"perfume", "accessories"},
        "perfume": {"perfumes", "accessories"},
        "wallets": {"wallet", "belts", "belt", "bags", "bag", "accessories", "keychains"},
        "wallet": {"wallets", "belts", "belt", "bags", "bag", "accessories", "keychains"},
        "belts": {"belt", "wallets", "wallet", "bags", "accessories"},
        "belt": {"belts", "wallets", "wallet", "bags", "accessories"},
        "bags": {"bag", "wallets", "wallet", "belts", "accessories"},
        "bag": {"bags", "wallets", "wallet", "belts", "accessories"},
        "caps": {"cap", "accessories", "sunglasses"},
        "cap": {"caps", "accessories", "sunglasses"},
        "sunglasses": {"caps", "cap", "accessories"},
        "lighters": {"lighter", "accessories", "keychains", "wallets"},
        "lighter": {"lighters", "accessories", "keychains", "wallets"},
        "keychains": {"keychain", "accessories", "wallets", "lighters"},
        "keychain": {"keychains", "accessories", "wallets", "lighters"},
        "shoes": {"accessories", "clothing", "pashtun_dress"},
        "shoe": {"shoes", "accessories", "clothing", "pashtun_dress"},
        "pashtun_dress": {"paint_shirt", "clothing", "accessories"},
        "paint_shirt": {"pashtun_dress", "clothing", "accessories"},
        "clothing": {"pashtun_dress", "paint_shirt", "accessories"},
        "accessories": {"wallets", "watches", "belts", "caps", "lighters", "keychains"},
    }

    scored = []
    for p in all_products:
        if p.get("id") == product_id:
            continue
        p_cat = (p.get("category") or "").lower().strip()
        score = 0
        reason = "Recommended for you"

        # 1. Exact Category match
        if p_cat == target_category or (target_category and p_cat and (target_category in p_cat or p_cat in target_category)):
            score += 15
            reason = "More from this collection"
        # 2. Related category cluster
        elif target_category in clusters and p_cat in clusters[target_category]:
            score += 7
            reason = "Complementary lifestyle essential"

        # 3. Tag matches
        p_tags = set(t.lower() for t in p.get("tags", []))
        shared_tags = target_tags.intersection(p_tags)
        if shared_tags:
            score += len(shared_tags) * 3

        # 4. Similar price range (within 35%)
        p_price = float(p.get("price", 0))
        if target_price > 0 and abs(p_price - target_price) / target_price <= 0.35:
            score += 3

        # 5. Bestseller / Featured bonus
        if p.get("is_bestseller"):
            score += 2
        if p.get("is_featured"):
            score += 1

        p_copy = dict(p)
        p_copy["recommendation_reason"] = reason
        scored.append((score, p_copy))

    # Sort by recommendation score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:limit]]
