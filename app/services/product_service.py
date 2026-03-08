# app/services/product_service.py
#
# Service layer: contains all business logic for products.
# Routes call services. Services talk to the database.
# This separation keeps routes thin and logic testable.

from typing import List, Optional
from datetime import datetime
from app.services.firebase_service import db
from app.schemas.product_schema import ProductCreate, ProductUpdate


COLLECTION = "products"


def get_all_products(
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    bestseller: Optional[bool] = None,
    limit: int = 50
) -> List[dict]:
    """
    Fetch products from Firestore with optional filters.
    
    How Firestore querying works:
    - Start with collection reference
    - Chain .where() filters
    - Call .get() to execute
    - Convert each document to dict and add the 'id' field
    """
    ref = db.collection(COLLECTION)

    # Apply filters if provided
    if category:
        ref = ref.where("category", "==", category)
    if featured is not None:
        ref = ref.where("is_featured", "==", featured)
    if bestseller is not None:
        ref = ref.where("is_bestseller", "==", bestseller)

    docs = ref.limit(limit).get()

    products = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id      # Firestore document ID
        products.append(data)

    return products


def get_product_by_id(product_id: str) -> Optional[dict]:
    """Fetch a single product by its Firestore document ID."""
    doc = db.collection(COLLECTION).document(product_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def create_product(product_data: ProductCreate) -> dict:
    """
    Create a new product in Firestore.
    
    Firestore auto-generates a document ID when we use .add()
    We return the created data including the new ID.
    """
    data = product_data.model_dump()
    data["created_at"] = datetime.utcnow().isoformat()
    data["updated_at"] = datetime.utcnow().isoformat()

    # .add() returns a tuple: (timestamp, document_reference)
    _, doc_ref = db.collection(COLLECTION).add(data)
    data["id"] = doc_ref.id
    return data


def update_product(product_id: str, update_data: ProductUpdate) -> Optional[dict]:
    """Update only the provided fields of a product."""
    doc_ref = db.collection(COLLECTION).document(product_id)
    if not doc_ref.get().exists:
        return None

    # model_dump(exclude_none=True) skips fields that are None
    # So we only update what was provided
    updates = update_data.model_dump(exclude_none=True)
    updates["updated_at"] = datetime.utcnow().isoformat()
    doc_ref.update(updates)

    updated = doc_ref.get().to_dict()
    updated["id"] = product_id
    return updated


def delete_product(product_id: str) -> bool:
    """Delete a product. Returns True if existed, False if not found."""
    doc_ref = db.collection(COLLECTION).document(product_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.delete()
    return True


def search_products(query: str) -> List[dict]:
    """
    Basic product search by name.
    
    Note: Firestore doesn't support full-text search natively.
    For production, consider Algolia or Firebase Extensions.
    This is a simple prefix match using range queries.
    """
    query_lower = query.lower()
    docs = db.collection(COLLECTION).get()

    results = []
    for doc in docs:
        data = doc.to_dict()
        name = data.get("name", "").lower()
        description = data.get("description", "").lower()
        tags = [t.lower() for t in data.get("tags", [])]

        if (query_lower in name or
                query_lower in description or
                any(query_lower in tag for tag in tags)):
            data["id"] = doc.id
            results.append(data)

    return results


def seed_sample_products():
    """
    Add sample products to Firestore for testing.
    Call this once to populate the database.
    
    Sample data includes Pashtun dresses and Paint Shirts.
    """
    sample_products = [
        {
            "name": "Traditional Pashtun Perahan Tunban",
            "description": "Authentic hand-embroidered Pashtun Perahan Tunban with intricate khamak (needlepoint) embroidery along the collar and cuffs. Made from premium lawn fabric, perfect for both daily wear and special occasions.",
            "price": 4500.0,
            "category": "pashtun_dress",
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "colors": ["White", "Cream", "Light Blue", "Sage Green"],
            "stock": 20,
            "image_urls": ["https://via.placeholder.com/600x800?text=Pashtun+Dress+1"],
            "is_featured": True,
            "is_bestseller": True,
            "tags": ["traditional", "embroidered", "pashtun", "perahan"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "Kandahari Chapan Coat",
            "description": "Elegant Kandahari-style chapan (long coat) with beautiful woven patterns. Traditionally worn at celebrations and gatherings. Made from high-quality velvet with silk lining.",
            "price": 8500.0,
            "category": "pashtun_dress",
            "sizes": ["M", "L", "XL", "XXL"],
            "colors": ["Navy Blue", "Deep Red", "Forest Green"],
            "stock": 10,
            "image_urls": ["https://via.placeholder.com/600x800?text=Chapan+Coat"],
            "is_featured": True,
            "is_bestseller": False,
            "tags": ["chapan", "coat", "traditional", "festive"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "Floral Hand-Painted Shirt",
            "description": "Unique hand-painted cotton shirt featuring traditional Pashtun floral motifs painted by local artisans. Each piece is one-of-a-kind. Machine washable, fade-resistant paint used.",
            "price": 2800.0,
            "category": "paint_shirt",
            "sizes": ["S", "M", "L", "XL"],
            "colors": ["White base with multicolor painting"],
            "stock": 15,
            "image_urls": ["https://via.placeholder.com/600x800?text=Paint+Shirt+1"],
            "is_featured": True,
            "is_bestseller": True,
            "tags": ["hand-painted", "floral", "artisan", "unique"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "Geometric Art Paint Shirt",
            "description": "Modern paint shirt featuring geometric Pashtun tribal patterns in bold colors. A fusion of traditional art and contemporary fashion. 100% cotton, comfortable fit.",
            "price": 2500.0,
            "category": "paint_shirt",
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "colors": ["White", "Black", "Grey"],
            "stock": 25,
            "image_urls": ["https://via.placeholder.com/600x800?text=Paint+Shirt+2"],
            "is_featured": False,
            "is_bestseller": True,
            "tags": ["geometric", "tribal", "modern", "cotton"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "Peshawari Khat Dress",
            "description": "Traditional Peshawari style dress with distinctive khat (striped) pattern. Lightweight and breathable fabric, ideal for summer. Features traditional collar embroidery.",
            "price": 3200.0,
            "category": "pashtun_dress",
            "sizes": ["S", "M", "L", "XL"],
            "colors": ["Blue Stripes", "Green Stripes", "Brown Stripes"],
            "stock": 18,
            "image_urls": ["https://via.placeholder.com/600x800?text=Khat+Dress"],
            "is_featured": False,
            "is_bestseller": False,
            "tags": ["peshawari", "khat", "striped", "summer"],
            "created_at": datetime.utcnow().isoformat()
        },
    ]

    batch = db.batch()
    for product in sample_products:
        doc_ref = db.collection(COLLECTION).document()
        batch.set(doc_ref, product)
    batch.commit()

    return {"seeded": len(sample_products), "message": "Sample products added successfully"}