# app/schemas/lookbook_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional

class LookbookHotspot(BaseModel):
    id: Optional[str] = None
    product_id: str
    position_x: float = Field(..., ge=0.0, le=100.0, description="Percentage position X (0-100)")
    position_y: float = Field(..., ge=0.0, le=100.0, description="Percentage position Y (0-100)")
    label: str = Field(..., description="Pin tooltip title or price tag")

class LookbookBase(BaseModel):
    title: str = Field(..., min_length=2)
    description: Optional[str] = None
    cover_image: str = Field(..., description="High resolution editorial image URL")
    status: str = Field("active", description="active | draft")
    sort_order: int = Field(0, description="Display sorting order")
    hotspots: List[LookbookHotspot] = []

class LookbookCreate(LookbookBase):
    pass

class LookbookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None
    hotspots: Optional[List[LookbookHotspot]] = None

class LookbookResponse(LookbookBase):
    id: str
    created_at: str
    updated_at: Optional[str] = None
