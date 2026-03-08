# app/services/product_service.py

from datetime import datetime
from typing import List, Optional
from app.services.firebase_service import get_all, get_one, create_one, update_one, delete_one
from app.schemas.product_schema import ProductCreate, ProductUpdate

COLLECTION = "products"


def get_all_products(category=None, featured=None, bestseller=None, limit=50) -> List[dict]:
    products = get_all(COLLECTION)
    if category:
        products = [p for p in products if p.get("category") == category]
    if featured is not None:
        products = [p for p in products if p.get("is_featured") == featured]
    if bestseller is not None:
        products = [p for p in products if p.get("is_bestseller") == bestseller]
    return products[:limit]


def get_product_by_id(product_id: str) -> Optional[dict]:
    return get_one(COLLECTION, product_id)


def create_product(product_data: ProductCreate) -> dict:
    data = product_data.model_dump()
    data["created_at"] = datetime.utcnow().isoformat()
    data["updated_at"] = datetime.utcnow().isoformat()
    return create_one(COLLECTION, data)


def update_product(product_id: str, update_data: ProductUpdate) -> Optional[dict]:
    updates = update_data.model_dump(exclude_none=True)
    updates["updated_at"] = datetime.utcnow().isoformat()
    return update_one(COLLECTION, product_id, updates)


def delete_product(product_id: str) -> bool:
    return delete_one(COLLECTION, product_id)


def search_products(query: str) -> List[dict]:
    products = get_all(COLLECTION)
    query_lower = query.lower()
    return [
        p for p in products
        if query_lower in p.get("name", "").lower()
        or query_lower in p.get("description", "").lower()
        or any(query_lower in t.lower() for t in p.get("tags", []))
    ]


def seed_sample_products():
    sample_products = [
        {
            "name": "Traditional Pashtun Perahan Tunban",
            "description": "Authentic hand-embroidered Pashtun Perahan Tunban with intricate khamak embroidery. Made from premium lawn fabric.",
            "price": 4500.0,
            "category": "pashtun_dress",
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "colors": ["White", "Cream", "Light Blue", "Sage Green"],
            "stock": 20,
            "image_urls": ["https://via.placeholder.com/600x800?text=Pashtun+Dress"],
            "is_featured": True,
            "is_bestseller": True,
            "tags": ["traditional", "embroidered", "pashtun"],
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "name": "Kandahari Chapan Coat",
            "description": "Elegant Kandahari-style chapan with beautiful woven patterns. Made from high-quality velvet with silk lining.",
            "price": 8500.0,
            "category": "pashtun_dress",
            "sizes": ["M", "L", "XL", "XXL"],
            "colors": ["Navy Blue", "Deep Red", "Forest Green"],
            "stock": 10,
            "image_urls": ["https://via.placeholder.com/600x800?text=Chapan+Coat"],
            "is_featured": True,
            "is_bestseller": False,
            "tags": ["chapan", "coat", "traditional"],
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "name": "Floral Hand-Painted Shirt",
            "description": "Unique hand-painted cotton shirt featuring traditional Pashtun floral motifs. Each piece is one-of-a-kind.",
            "price": 2800.0,
            "category": "paint_shirt",
            "sizes": ["S", "M", "L", "XL"],
            "colors": ["White base with multicolor painting"],
            "stock": 15,
            "image_urls": ["https://via.placeholder.com/600x800?text=Paint+Shirt+1"],
            "is_featured": True,
            "is_bestseller": True,
            "tags": ["hand-painted", "floral", "artisan"],
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "name": "Geometric Art Paint Shirt",
            "description": "Modern paint shirt featuring geometric Pashtun tribal patterns. 100% cotton, comfortable fit.",
            "price": 2500.0,
            "category": "paint_shirt",
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "colors": ["White", "Black", "Grey"],
            "stock": 25,
            "image_urls": ["https://via.placeholder.com/600x800?text=Paint+Shirt+2"],
            "is_featured": False,
            "is_bestseller": True,
            "tags": ["geometric", "tribal", "modern"],
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "name": "Peshawari Khat Dress",
            "description": "Traditional Peshawari style dress with distinctive khat striped pattern. Lightweight and breathable.",
            "price": 3200.0,
            "category": "pashtun_dress",
            "sizes": ["S", "M", "L", "XL"],
            "colors": ["Blue Stripes", "Green Stripes", "Brown Stripes"],
            "stock": 18,
            "image_urls": ["https://via.placeholder.com/600x800?text=Khat+Dress"],
            "is_featured": False,
            "is_bestseller": False,
            "tags": ["peshawari", "khat", "striped"],
            "created_at": datetime.utcnow().isoformat(),
        },
    ]

    for product in sample_products:
        create_one(COLLECTION, product)

    return {"seeded": len(sample_products), "message": "Sample products added successfully"}