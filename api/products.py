# api/products.py

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Header, Body, Request
from typing import Optional, List
from datetime import datetime
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.services import product_service, auth_service
from app.services.firebase_service import get_all, get_one, create_one, update_one

router = APIRouter()


def _require_admin(authorization: Optional[str]) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")

    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)

    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return user


@router.get("/", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    featured: Optional[bool] = Query(None, description="Filter featured products"),
    bestseller: Optional[bool] = Query(None, description="Filter bestsellers"),
    limit: int = Query(50, le=200, description="Max number of products to return"),
):
    return product_service.get_all_products(
        category=category,
        featured=featured,
        bestseller=bestseller,
        limit=limit
    )


@router.get("/search", response_model=List[ProductResponse])
def search_products(q: str = Query(..., min_length=2, description="Search keyword")):
    return product_service.search_products(q)


@router.get("/community/gallery")
def get_community_gallery():
    """Get approved community styled fashion photos."""
    gallery = get_all("community_gallery")
    if not gallery:
        # Sample fallback community gallery items
        return [
            {
                "id": "cg1",
                "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=600&q=80",
                "customer_name": "Amina K.",
                "caption": "Peshawar Heritage Dress styled for Eid celebration! ✨",
                "product_name": "Traditional Pashtun Perahan Tunban",
                "product_id": "p1"
            },
            {
                "id": "cg2",
                "image_url": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=600&q=80",
                "customer_name": "Zuhra P.",
                "caption": "Hand-painted floral motifs in full glow.",
                "product_name": "Floral Hand-Painted Shirt",
                "product_id": "p3"
            },
            {
                "id": "cg3",
                "image_url": "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=600&q=80",
                "customer_name": "Bilal A.",
                "caption": "Kandahari Chapan Coat at the evening gala.",
                "product_name": "Kandahari Chapan Coat",
                "product_id": "p2"
            }
        ]
    return gallery


@router.post("/community/gallery")
def submit_community_photo(data: dict = Body(...)):
    """Submit customer photo for community approval."""
    photo_data = {
        "image_url": data.get("image_url", ""),
        "customer_name": data.get("customer_name", "Anonymous Patron"),
        "caption": data.get("caption", ""),
        "product_id": data.get("product_id", ""),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    created = create_one("community_gallery", photo_data)
    return {"message": "Thank you! Your photo was submitted for review.", "item": created}


@router.get("/{product_id}/complete-the-look", response_model=List[ProductResponse])
def get_complete_the_look(product_id: str):
    """Get recommended bundle items to complete the outfit."""
    from app.services.recommendation_service import get_complete_the_look as fetch_bundle
    return fetch_bundle(product_id)


@router.post("/{product_id}/complete-look")
def set_complete_the_look_items(
    product_id: str,
    data: dict = Body(...),
    authorization: Optional[str] = Header(None)
):
    """Admin: Configure paired product IDs for complete the look bundle."""
    _require_admin(authorization)
    item_ids = data.get("item_ids", [])
    if not isinstance(item_ids, list):
        raise HTTPException(status_code=400, detail="item_ids must be a list of product IDs")

    updated = update_one("products", product_id, {
        "complete_the_look_ids": item_ids,
        "updated_at": datetime.utcnow().isoformat()
    })
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Complete the look relations updated", "item_ids": item_ids}


@router.get("/{product_id}/recommendations", response_model=List[ProductResponse])
def get_recommendations(product_id: str):
    """Get smart recommendations (You May Also Like / Customers Loved)."""
    from app.services.recommendation_service import get_smart_recommendations as fetch_recs
    return fetch_recs(product_id)


@router.post("/{product_id}/notify")
def request_notification(product_id: str, data: dict = Body(...)):
    """Register alert for back in stock or price drop."""
    email = data.get("email", "").strip()
    notify_type = data.get("notify_type", "back_in_stock")
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")

    alert_data = {
        "product_id": product_id,
        "email": email,
        "notify_type": notify_type,
        "created_at": datetime.utcnow().isoformat()
    }
    create_one("notifications", alert_data)
    return {"message": f"Alert registered successfully for {notify_type.replace('_', ' ')}!"}


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str):
    product = product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, authorization: Optional[str] = Header(None)):
    _require_admin(authorization)
    return product_service.create_product(product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    update_data: ProductUpdate,
    authorization: Optional[str] = Header(None),
):
    _require_admin(authorization)
    updated = product_service.update_product(product_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated


@router.delete("/{product_id}")
def delete_product(product_id: str, authorization: Optional[str] = Header(None)):
    _require_admin(authorization)
    success = product_service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@router.post("/seed/sample-data")
def seed_products(authorization: Optional[str] = Header(None)):
    _require_admin(authorization)
    return product_service.seed_sample_products()


@router.post("/upload-image")
async def upload_generic_product_image(
    request: Request,
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
):
    """Generic image upload for products before they are created."""
    _require_admin(authorization)
    from app.services.local_storage_service import save_local_image

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        filename = f"products/img_{int(datetime.utcnow().timestamp())}_{file.filename}"
        public_url = save_local_image(content, filename, request)
        return {"image_url": public_url, "message": "Image uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

@router.post("/{product_id}/upload-image")
async def upload_product_image(
    request: Request,
    product_id: str,
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
):
    _require_admin(authorization)
    from app.services.firebase_service import get_one, update_one
    from app.services.local_storage_service import save_local_image

    product = get_one("products", product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    content = await file.read()
    try:
        filename = f"{product_id}_{file.filename}"
        public_url = save_local_image(content, f"products/{filename}", request)

        current_urls = product.get("image_urls", [])
        current_urls.append(public_url)
        update_one("products", product_id, {"image_urls": current_urls})

        return {"image_url": public_url, "message": "Image uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")