# app/services/wishlist_service.py
#
# One wishlist document per user, keyed by user_id, holding a list of
# product IDs. Kept intentionally simple — same style as the rest of
# the service layer (plain dicts in/out, no separate schema needed
# since routes only ever return product IDs or full Product objects).

from typing import List
from app.services.firebase_service import get_one, set_one
from app.services import product_service

COLLECTION = "wishlists"


def get_wishlist_ids(user_id: str) -> List[str]:
    """Return the raw list of product IDs a user has wishlisted."""
    doc = get_one(COLLECTION, user_id)
    return doc.get("product_ids", []) if doc else []


def get_wishlist_products(user_id: str) -> List[dict]:
    """Return the user's wishlisted products, resolved to full Product dicts.

    Silently skips any ID whose product has since been deleted, so a
    stale wishlist entry never breaks the listing.
    """
    ids = get_wishlist_ids(user_id)
    products = [product_service.get_product_by_id(pid) for pid in ids]
    return [p for p in products if p is not None]


def add_to_wishlist(user_id: str, product_id: str) -> List[str]:
    """Add a product to the user's wishlist. No-op if already present."""
    ids = get_wishlist_ids(user_id)
    if product_id not in ids:
        ids.append(product_id)
        set_one(COLLECTION, user_id, {"product_ids": ids})
    return ids


def remove_from_wishlist(user_id: str, product_id: str) -> List[str]:
    """Remove a product from the user's wishlist. No-op if not present."""
    ids = get_wishlist_ids(user_id)
    if product_id in ids:
        ids.remove(product_id)
        set_one(COLLECTION, user_id, {"product_ids": ids})
    return ids
