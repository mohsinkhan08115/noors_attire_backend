# api/wishlist.py

from fastapi import APIRouter, HTTPException, Header, Body
from typing import Optional, List
from app.schemas.product_schema import ProductResponse
from app.services import wishlist_service, auth_service, product_service
from app.services.firebase_service import get_one, set_one

router = APIRouter()


def _get_authenticated_user(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


@router.get("/", response_model=List[ProductResponse])
def get_wishlist(authorization: Optional[str] = Header(None)):
    user = _get_authenticated_user(authorization)
    return wishlist_service.get_wishlist_products(user["id"])


@router.post("/{product_id}", response_model=List[ProductResponse])
def add_to_wishlist(product_id: str, authorization: Optional[str] = Header(None)):
    user = _get_authenticated_user(authorization)
    if not product_service.get_product_by_id(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    wishlist_service.add_to_wishlist(user["id"], product_id)
    return wishlist_service.get_wishlist_products(user["id"])


@router.delete("/{product_id}", response_model=List[ProductResponse])
def remove_from_wishlist(product_id: str, authorization: Optional[str] = Header(None)):
    user = _get_authenticated_user(authorization)
    wishlist_service.remove_from_wishlist(user["id"], product_id)
    return wishlist_service.get_wishlist_products(user["id"])


# ── Smart Wishlist Collections Endpoints ─────────────────────────────────────

@router.get("/collections")
def get_collections(authorization: Optional[str] = Header(None)):
    """Get the user's custom wishlist collections."""
    user = _get_authenticated_user(authorization)
    doc = get_one("wishlist_collections", user["id"])
    if not doc:
        # Default collections
        return {
            "Wedding": [],
            "Eid": [],
            "Casual": [],
            "Gifts": [],
            "Favorites": [],
            "Maybe Later": []
        }
    return doc.get("collections", {})


@router.post("/collections")
def create_collection(data: dict = Body(...), authorization: Optional[str] = Header(None)):
    """Create a new custom wishlist collection."""
    user = _get_authenticated_user(authorization)
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Collection name is required")

    doc = get_one("wishlist_collections", user["id"]) or {"collections": {}}
    collections = doc.get("collections", {})
    if name not in collections:
        collections[name] = []
    set_one("wishlist_collections", user["id"], {"collections": collections})
    return {"message": f"Collection '{name}' created successfully", "collections": collections}


@router.post("/collections/{collection_name}/items")
def add_item_to_collection(
    collection_name: str,
    data: dict = Body(...),
    authorization: Optional[str] = Header(None)
):
    """Add product ID to a named collection."""
    user = _get_authenticated_user(authorization)
    product_id = data.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="Product ID required")

    doc = get_one("wishlist_collections", user["id"]) or {"collections": {}}
    collections = doc.get("collections", {})
    if collection_name not in collections:
        collections[collection_name] = []
    if product_id not in collections[collection_name]:
        collections[collection_name].append(product_id)

    set_one("wishlist_collections", user["id"], {"collections": collections})
    return {"message": f"Product added to {collection_name}", "collections": collections}


@router.put("/collections/{collection_name}")
def rename_collection(
    collection_name: str,
    data: dict = Body(...),
    authorization: Optional[str] = Header(None)
):
    """Rename a custom collection."""
    user = _get_authenticated_user(authorization)
    new_name = data.get("new_name", "").strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="New collection name is required")

    doc = get_one("wishlist_collections", user["id"]) or {"collections": {}}
    collections = doc.get("collections", {})
    if collection_name in collections:
        items = collections.pop(collection_name)
        collections[new_name] = items
        set_one("wishlist_collections", user["id"], {"collections": collections})
    return {"message": f"Collection renamed to '{new_name}'", "collections": collections}


@router.delete("/collections/{collection_name}")
def delete_collection(
    collection_name: str,
    authorization: Optional[str] = Header(None)
):
    """Delete a custom collection board."""
    user = _get_authenticated_user(authorization)
    doc = get_one("wishlist_collections", user["id"]) or {"collections": {}}
    collections = doc.get("collections", {})
    if collection_name in collections:
        collections.pop(collection_name)
        set_one("wishlist_collections", user["id"], {"collections": collections})
    return {"message": f"Collection '{collection_name}' deleted", "collections": collections}


@router.put("/items/{product_id}/collection")
def move_item_collection(
    product_id: str,
    data: dict = Body(...),
    authorization: Optional[str] = Header(None)
):
    """Move product item to target collection."""
    user = _get_authenticated_user(authorization)
    target_collection = data.get("target_collection", "").strip()
    if not target_collection:
        raise HTTPException(status_code=400, detail="target_collection required")

    doc = get_one("wishlist_collections", user["id"]) or {"collections": {}}
    collections = doc.get("collections", {})

    # Remove product from any existing collection
    for col_name, item_list in collections.items():
        if product_id in item_list:
            item_list.remove(product_id)

    # Add to target collection
    if target_collection not in collections:
        collections[target_collection] = []
    collections[target_collection].append(product_id)

    set_one("wishlist_collections", user["id"], {"collections": collections})
    return {"message": f"Item moved to {target_collection}", "collections": collections}
