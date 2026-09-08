# app/services/variant_service.py

from typing import List, Dict, Any
from datetime import datetime
from app.schemas.variant_schema import VariantCreate, VariantUpdate
from app.services.firebase_service import get_one, update_one, set_one
from app.services.alert_service import trigger_stock_replenishment_notifications

def get_product_variants(product_id: str) -> List[Dict[str, Any]]:
    product = get_one("products", product_id)
    if not product:
        return []
    return product.get("variants", [])


def add_product_variant(product_id: str, variant: VariantCreate) -> Dict[str, Any]:
    product = get_one("products", product_id)
    if not product:
        raise ValueError("Product not found")

    variants = product.get("variants", [])
    import uuid
    new_variant = {
        "id": f"var_{uuid.uuid4().hex[:8]}",
        "product_id": product_id,
        "size": variant.size,
        "color": variant.color,
        "sku": variant.sku or f"{product_id}-{variant.size}-{variant.color}",
        "price": variant.price,
        "stock": variant.stock,
        "image_url": variant.image_url,
        "status": variant.status if variant.stock > 0 else "out_of_stock",
    }
    variants.append(new_variant)
    update_one("products", product_id, {"variants": variants, "updated_at": datetime.utcnow().isoformat()})
    return new_variant


def update_product_variant(product_id: str, variant_id: str, update_data: VariantUpdate) -> Dict[str, Any] | None:
    product = get_one("products", product_id)
    if not product:
        return None

    variants = product.get("variants", [])
    target = None
    old_stock = 0

    for v in variants:
        if v.get("id") == variant_id:
            target = v
            old_stock = v.get("stock", 0)
            break

    if not target:
        return None

    data_dict = update_data.model_dump(exclude_unset=True)
    target.update(data_dict)

    new_stock = target.get("stock", old_stock)
    if new_stock > 0 and old_stock == 0:
        target["status"] = "active"
        trigger_stock_replenishment_notifications(product_id, new_stock)
    elif new_stock <= 0:
        target["status"] = "out_of_stock"

    update_one("products", product_id, {"variants": variants, "updated_at": datetime.utcnow().isoformat()})
    return target


def delete_product_variant(product_id: str, variant_id: str) -> bool:
    product = get_one("products", product_id)
    if not product:
        return False

    variants = product.get("variants", [])
    filtered = [v for v in variants if v.get("id") != variant_id]
    if len(filtered) == len(variants):
        return False

    update_one("products", product_id, {"variants": filtered, "updated_at": datetime.utcnow().isoformat()})
    return True
