# app/schemas/order_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderItem(BaseModel):
    """A single item in an order."""
    product_id: str
    product_name: str
    quantity: int = Field(..., ge=1)
    price: float
    size: Optional[str] = None
    color: Optional[str] = None


class ShippingAddress(BaseModel):
    """Delivery address for an order."""
    full_name: str
    phone: str
    address: str
    city: str
    province: str
    postal_code: Optional[str] = None


class GiftInfo(BaseModel):
    """Gift Mode checkout options."""
    is_gift: bool = True
    recipient_name: Optional[str] = None
    gift_message: Optional[str] = None
    gift_packaging: Optional[str] = None
    packaging_fee: Optional[float] = 0.0
    requested_delivery_date: Optional[str] = None


class OrderCreate(BaseModel):
    """Data required to place an order."""
    items: List[OrderItem]
    shipping_address: ShippingAddress
    payment_method: str = "cash_on_delivery"
    notes: Optional[str] = None
    gift_info: Optional[GiftInfo] = None


class OrderResponse(BaseModel):
    """Order data returned to client."""
    id: str
    user_id: str
    items: List[OrderItem]
    shipping_address: ShippingAddress
    total_amount: float
    status: OrderStatus
    payment_method: str
    notes: Optional[str] = None
    gift_info: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None