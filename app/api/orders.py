# api/orders.py
#
# Order endpoints. All require authentication.
# POST /orders           → place new order
# GET  /orders           → get my orders
# GET  /orders/{id}      → get single order
# PUT  /orders/{id}/status → update status (admin)

from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
from app.schemas.order_schema import OrderCreate, OrderResponse, OrderStatus
from app.services import order_service, auth_service

router = APIRouter()


def _get_authenticated_user(authorization: Optional[str]):
    """
    Helper: extract user from Authorization header.
    Raises 401 if not authenticated.
    Used by every protected endpoint in this file.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")

    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    order_data: OrderCreate,
    authorization: Optional[str] = Header(None)
):
    """
    Place a new order. Requires login.
    
    The cart data from Flutter is sent as the request body.
    The total is calculated server-side to prevent tampering.
    
    Request example:
    {
      "items": [
        {
          "product_id": "abc123",
          "product_name": "Pashtun Perahan",
          "quantity": 2,
          "price": 4500.0,
          "size": "M",
          "color": "White"
        }
      ],
      "shipping_address": {
        "full_name": "Noor Ahmed",
        "phone": "+92300000000",
        "address": "House 12, Street 5",
        "city": "Peshawar",
        "province": "KPK"
      },
      "payment_method": "cash_on_delivery"
    }
    """
    user = _get_authenticated_user(authorization)
    return order_service.create_order(user["id"], order_data)


@router.get("/", response_model=List[OrderResponse])
def get_my_orders(authorization: Optional[str] = Header(None)):
    """
    Get all orders for the logged-in user.
    Returned newest first.
    """
    user = _get_authenticated_user(authorization)
    return order_service.get_user_orders(user["id"])


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, authorization: Optional[str] = Header(None)):
    """
    Get a specific order by ID.
    Users can only see their own orders.
    """
    user = _get_authenticated_user(authorization)
    order = order_service.get_order_by_id(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Security check: only the order owner can view it
    if order["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    return order


@router.put("/{order_id}/status")
def update_order_status(
    order_id: str,
    status: OrderStatus,
    authorization: Optional[str] = Header(None)
):
    """
    Update order status. (Admin function)
    Valid statuses: pending, confirmed, shipped, delivered, cancelled
    """
    _get_authenticated_user(authorization)  # Auth check
    updated = order_service.update_order_status(order_id, status)

    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": f"Order status updated to {status}", "order": updated}