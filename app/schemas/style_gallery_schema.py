# app/schemas/style_gallery_schema.py

from pydantic import BaseModel, Field
from typing import Optional

class StyleSubmissionCreate(BaseModel):
    image_url: str = Field(..., description="Uploaded customer outfit photo URL")
    caption: Optional[str] = Field(None, description="Customer outfit description")
    product_id: Optional[str] = Field(None, description="Tagged dress or shirt product ID")
    customer_name: Optional[str] = Field("Anonymous Patron", description="Display name or social handle")

class StyleSubmissionResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    image_url: str
    caption: Optional[str] = None
    product_id: Optional[str] = None
    customer_name: str
    status: str = Field("pending", description="pending | approved | rejected")
    created_at: str
    updated_at: Optional[str] = None
