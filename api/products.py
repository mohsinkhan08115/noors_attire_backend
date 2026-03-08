# api/products.py
#
# Product endpoints. Each function handles one HTTP route.
# Routes call the service layer — they don't touch the database directly.
#
# Endpoints:
#   GET  /products              → list all (with optional filters)
#   GET  /products/search       → search by keyword  
#   GET  /products/{id}         → single product
#   POST /products              → create product (admin)
#   PUT  /products/{id}         → update product (admin)
#   DELETE /products/{id}       → delete product (admin)
#   POST /products/seed         → add sample data

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Optional, List
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.services import product_service

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = Query(None, description="Filter by category: pashtun_dress or paint_shirt"),
    featured: Optional[bool] = Query(None, description="Filter featured products"),
    bestseller: Optional[bool] = Query(None, description="Filter bestsellers"),
    limit: int = Query(50, le=200, description="Max number of products to return"),
):
    """
    Get all products with optional filters.
    
    Examples:
      GET /products                          → all products
      GET /products?category=pashtun_dress   → only Pashtun dresses
      GET /products?featured=true            → featured products for homepage
      GET /products?bestseller=true          → bestsellers section
    
    Sample response:
    [
      {
        "id": "abc123",
        "name": "Traditional Pashtun Perahan",
        "price": 4500.0,
        "category": "pashtun_dress",
        "image_urls": ["https://..."],
        "is_featured": true,
        ...
      }
    ]
    """
    return product_service.get_all_products(
        category=category,
        featured=featured,
        bestseller=bestseller,
        limit=limit
    )


@router.get("/search", response_model=List[ProductResponse])
def search_products(q: str = Query(..., min_length=2, description="Search keyword")):
    """
    Search products by name, description, or tags.
    
    Example: GET /products/search?q=embroidered
    """
    return product_service.search_products(q)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str):
    """
    Get a single product by ID.
    
    Returns 404 if the product doesn't exist.
    """
    product = product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate):
    """
    Create a new product. (Admin only in production)
    
    Returns the created product with its new Firestore ID.
    Status 201 = Created successfully.
    """
    return product_service.create_product(product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, update_data: ProductUpdate):
    """
    Update an existing product.
    Only the fields you provide will be changed.
    """
    updated = product_service.update_product(product_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated


@router.delete("/{product_id}")
def delete_product(product_id: str):
    """Delete a product permanently."""
    success = product_service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@router.post("/seed/sample-data")
def seed_products():
    """
    Seed the database with sample Pashtun dresses and Paint Shirts.
    Call this once to populate your store for testing.
    """
    return product_service.seed_sample_products()


@router.post("/{product_id}/upload-image")
async def upload_product_image(product_id: str, file: UploadFile = File(...)):
    """
    Upload a product image to Firebase Storage.
    
    How it works:
    1. Read the uploaded file bytes
    2. Upload to Firebase Storage under 'products/filename'
    3. Get the public URL
    4. Add URL to the product's image_urls list in Firestore
    """
    from app.services.firebase_service import upload_image, db

    # Read file content
    content = await file.read()

    # Upload to Firebase Storage
    filename = f"{product_id}_{file.filename}"
    public_url = upload_image(content, filename, file.content_type)

    # Add URL to product document
    doc_ref = db.collection("products").document(product_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Product not found")

    current_urls = doc.to_dict().get("image_urls", [])
    current_urls.append(public_url)
    doc_ref.update({"image_urls": current_urls})

    return {"image_url": public_url, "message": "Image uploaded successfully"}