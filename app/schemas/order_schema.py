# app/schemas/order_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional
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


class OrderCreate(BaseModel):
    """Data required to place an order."""
    items: List[OrderItem]
    shipping_address: ShippingAddress
    payment_method: str = "cash_on_delivery"
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "product_id": "abc123",
                        "product_name": "Traditional Pashtun Perahan",
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
        }


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
    created_at: Optional[str] = None