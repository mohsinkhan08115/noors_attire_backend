# app/schemas/look_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional

class LookItem(BaseModel):
    product_id: str
    role: str = Field(..., description="Role in outfit: main | accessory | footwear | shawl")
    is_optional: bool = False

class LookBase(BaseModel):
    title: str = Field(..., min_length=2)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    category: Optional[str] = Field("Bridal & Festive", description="Occasion category")
    items: List[LookItem] = []
    status: str = Field("active", description="active | draft | archived")

class LookCreate(LookBase):
    pass

class LookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    category: Optional[str] = None
    items: Optional[List[LookItem]] = None
    status: Optional[str] = None

class LookResponse(LookBase):
    id: str
    created_at: str
    updated_at: Optional[str] = None
