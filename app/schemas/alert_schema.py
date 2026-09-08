# app/schemas/alert_schema.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class StockAlertCreate(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    email: EmailStr

class PriceAlertCreate(BaseModel):
    product_id: str
    target_price: Optional[float] = Field(None, gt=0, description="Alert when price drops to or below target")
    email: EmailStr

class AlertResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    email: str
    product_id: str
    variant_id: Optional[str] = None
    target_price: Optional[float] = None
    alert_type: str = Field(..., description="back_in_stock | price_drop")
    status: str = Field("active", description="active | triggered | cancelled")
    created_at: str
