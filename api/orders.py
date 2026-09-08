# api/orders.py
from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.order_schema import OrderCreate, OrderResponse, OrderStatus
from app.services import order_service, auth_service

router = APIRouter()

class StatusUpdate(BaseModel):
    status: str

def _get_authenticated_user(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def _require_admin(authorization: Optional[str]):
    """Stricter guard for routes that must not leak other customers' orders."""
    user = _get_authenticated_user(authorization)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(order_data: OrderCreate, authorization: Optional[str] = Header(None)):
    user = _get_authenticated_user(authorization)
    return order_service.create_order(user["id"], order_data)

@router.get("/all")
def get_all_orders(authorization: Optional[str] = Header(None)):
    """Admin only — lists every customer's orders. Use /admin/orders instead where possible."""
    _require_admin(authorization)
    from app.services.firebase_service import get_all
    return get_all("orders")

@router.get("/", response_model=List[OrderResponse])
def get_my_orders(authorization: Optional[str] = Header(None)):
    user = _get_authenticated_user(authorization)
    return order_service.get_user_orders(user["id"])

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, authorization: Optional[str] = Header(None)):
    user = _get_authenticated_user(authorization)
    order = order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return order

@router.put("/{order_id}/status")
def update_order_status(order_id: str, data: StatusUpdate, authorization: Optional[str] = Header(None)):
    """Admin only — customers cannot change order status (including their own or others')."""
    _require_admin(authorization)
    updated = order_service.update_order_status(order_id, data.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": f"Order status updated to {data.status}", "order": updated}