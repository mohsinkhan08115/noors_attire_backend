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


def get_smart_recommendations(product_id: str, limit: int = 4) -> List[Dict[str, Any]]:
    """
    Rule-based recommendations based on category, price range, and tag matching.
    """
    target = get_one("products", product_id)
    all_products = get_all("products")
    if not target:
        return [p for p in all_products if p.get("id") != product_id][:limit]

    target_category = target.get("category")
    target_price = float(target.get("price", 0))
    
    scored = []
    for p in all_products:
        if p.get("id") == product_id:
            continue
        score = 0
        reason = "Recommended for you"

        # Category match
        if p.get("category") == target_category:
            score += 5
            reason = f"More from {target.get('category_name', 'this collection')}"

        # Similar price range (within 30%)
        p_price = float(p.get("price", 0))
        if target_price > 0 and abs(p_price - target_price) / target_price <= 0.3:
            score += 3

        # Bestseller / Featured bonus
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
