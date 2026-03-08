# app/services/order_service.py

from datetime import datetime
from typing import List, Optional
from app.services.firebase_service import get_all, get_one, create_one, update_one, query_by_field
from app.schemas.order_schema import OrderCreate, OrderStatus

COLLECTION = "orders"


def create_order(user_id: str, order_data: OrderCreate) -> dict:
    total = sum(item.price * item.quantity for item in order_data.items)

    order_dict = {
        "user_id": user_id,
        "items": [item.model_dump() for item in order_data.items],
        "shipping_address": order_data.shipping_address.model_dump(),
        "total_amount": round(total, 2),
        "status": OrderStatus.pending.value,
        "payment_method": order_data.payment_method,
        "notes": order_data.notes,
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
        "status": new_status.value,
        "updated_at": datetime.utcnow().isoformat()
    })