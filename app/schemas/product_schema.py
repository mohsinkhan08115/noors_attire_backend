# app/schemas/product_schema.py
#
# Pydantic schemas define the shape of data going IN and OUT of our API.
# They automatically validate data and generate API documentation.
#
# Think of schemas as contracts:
#   - Request schemas: what the client MUST send
#   - Response schemas: what we ALWAYS return

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class CategoryEnum(str, Enum):
    """Valid product categories for Noor's Attire."""
    pashtun_dress = "pashtun_dress"
    paint_shirt = "paint_shirt"
    accessories = "accessories"


class ProductCreate(BaseModel):
    """Schema for creating a new product (admin only)."""
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10)
    price: float = Field(..., gt=0)                  # gt=0 means price > 0
    category: CategoryEnum
    sizes: List[str] = Field(default=["S", "M", "L", "XL"])
    colors: List[str] = Field(default=[])
    stock: int = Field(default=0, ge=0)              # ge=0 means stock >= 0
    image_urls: List[str] = Field(default=[])
    is_featured: bool = False
    is_bestseller: bool = False
    tags: List[str] = Field(default=[])

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Traditional Pashtun Perahan",
                "description": "Hand-embroidered traditional Pashtun dress with gold khamak work",
                "price": 4500.0,
                "category": "pashtun_dress",
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["White", "Green", "Navy"],
                "stock": 15,
                "is_featured": True
            }
        }


class ProductUpdate(BaseModel):
    """Schema for updating a product — all fields optional."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[CategoryEnum] = None
    sizes: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    stock: Optional[int] = None
    image_urls: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_bestseller: Optional[bool] = None
    tags: Optional[List[str]] = None


class ProductResponse(BaseModel):
    """Schema for product data returned to the client."""
    id: str
    name: str
    description: str
    price: float
    category: str
    sizes: List[str]
    colors: List[str]
    stock: int
    image_urls: List[str]
    is_featured: bool
    is_bestseller: bool
    tags: List[str]
    created_at: Optional[str] = None

    class Config:
        from_attributes = True