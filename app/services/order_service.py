# app/services/order_service.py
#
# Handles all order-related business logic.
# When a customer checks out, this service:
# 1. Validates the cart items still exist
# 2. Calculates the total
# 3. Saves the order to Firestore
# 4. (Future) Sends confirmation email, reduces stock

from typing import List, Optional
from datetime import datetime
from app.services.firebase_service import db
from app.schemas.order_schema import OrderCreate, OrderStatus


COLLECTION = "orders"


def create_order(user_id: str, order_data: OrderCreate) -> dict:
    """
    Place a new order.
    
    Calculates total from items, sets initial status to 'pending',
    and saves everything to Firestore.
    """
    # Calculate total amount from all items
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

    _, doc_ref = db.collection(COLLECTION).add(order_dict)
    order_dict["id"] = doc_ref.id
    return order_dict


def get_user_orders(user_id: str) -> List[dict]:
    """Fetch all orders for a specific user, newest first."""
    docs = (
        db.collection(COLLECTION)
        .where("user_id", "==", user_id)
        .get()
    )

    orders = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        orders.append(data)

    # Sort by created_at descending (newest first)
    orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return orders


def get_order_by_id(order_id: str) -> Optional[dict]:
    """Fetch a single order by ID."""
    doc = db.collection(COLLECTION).document(order_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def update_order_status(order_id: str, new_status: OrderStatus) -> Optional[dict]:
    """Update the status of an order (admin function)."""
    doc_ref = db.collection(COLLECTION).document(order_id)
    if not doc_ref.get().exists:
        return None

    doc_ref.update({
        "status": new_status.value,
        "updated_at": datetime.utcnow().isoformat()
    })

    updated = doc_ref.get().to_dict()
    updated["id"] = order_id
    return updated