# app/services/order_service.py

from datetime import datetime
from typing import List, Optional
from app.services.firebase_service import get_all, get_one, create_one, update_one, query_by_field
from app.schemas.order_schema import OrderCreate, OrderStatus

COLLECTION = "orders"


def create_order(user_id: str, order_data: OrderCreate) -> dict:
    total = 0.0
    validated_items = []

    for item in order_data.items:
        product = get_one("products", item.product_id)
        if not product:
            # Fallback to submitted price if legacy or custom product
            item_price = float(item.price)
        else:
            # Server-side price calculation: check variant or product effective price
            item_price = float(product.get("price", item.price))
            if product.get("isOnSale") and product.get("discountPercent"):
                item_price = round(item_price * (1 - float(product.get("discountPercent")) / 100), 2)

            # Deduct stock server-side
            current_stock = int(product.get("stock", 0))
            if current_stock >= item.quantity:
                update_one("products", item.product_id, {"stock": current_stock - item.quantity})

        item_subtotal = item_price * item.quantity
        total += item_subtotal

        item_dict = item.model_dump()
        item_dict["price"] = item_price
        validated_items.append(item_dict)

    # Gift mode fee addition (+500 PKR if gift packaging requested)
    gift_dict = None
    if order_data.gift_info and order_data.gift_info.is_gift:
        packaging_fee = 500.0
        total += packaging_fee
        gift_dict = order_data.gift_info.model_dump()
        gift_dict["packaging_fee"] = packaging_fee

    order_dict = {
        "user_id": user_id,
        "items": validated_items,
        "shipping_address": order_data.shipping_address.model_dump(),
        "total_amount": round(total, 2),
        "status": OrderStatus.pending.value,
        "payment_method": order_data.payment_method,
        "notes": order_data.notes,
        "gift_info": gift_dict,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    return create_one(COLLECTION, order_dict)


def get_user_orders(user_id: str) -> List[dict]:
    orders = query_by_field(COLLECTION, "user_id", user_id)
    orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return orders


def get_order_by_id(order_id: str) -> Optional[dict]:
    return get_one(COLLECTION, order_id)


def update_order_status(order_id: str, new_status: OrderStatus) -> Optional[dict]:
    return update_one(COLLECTION, order_id, {
        "status": str(new_status),
        "updated_at": datetime.utcnow().isoformat()
    })