# app/schemas/variant_schema.py

from pydantic import BaseModel, Field
from typing import Optional

class VariantBase(BaseModel):
    size: str = Field(..., description="Variant size e.g. S, M, L, XL")
    color: str = Field(..., description="Variant color name e.g. Royal Maroon, Gold")
    sku: Optional[str] = Field(None, description="Stock Keeping Unit")
    price: Optional[float] = Field(None, description="Variant override price")
    stock: int = Field(0, ge=0, description="Available inventory count")
    image_url: Optional[str] = Field(None, description="Variant specific image URL")
    status: str = Field("active", description="Status: active | out_of_stock | disabled")

class VariantCreate(VariantBase):
    pass

class VariantUpdate(BaseModel):
    size: Optional[str] = None
    color: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    status: Optional[str] = None

class VariantResponse(VariantBase):
    id: str
    product_id: str
