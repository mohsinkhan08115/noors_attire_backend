from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class CategoryEnum(str, Enum):
    pashtun_dress = "pashtun_dress"
    paint_shirt = "paint_shirt"
    accessories = "accessories"

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10)
    price: float = Field(..., gt=0)
    sale_price: Optional[float] = Field(None, gt=0, description="Discounted price, if the product is on sale. Must be lower than price.")
    sku: Optional[str] = Field(None, max_length=50)
    category: CategoryEnum
    sizes: List[str] = Field(default=["S", "M", "L", "XL"])
    colors: List[str] = Field(default=[])
    stock: int = Field(default=0, ge=0)
    image_urls: List[str] = Field(default=[])
    is_featured: bool = False
    is_bestseller: bool = False
    tags: List[str] = Field(default=[])

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    sku: Optional[str] = None
    category: Optional[CategoryEnum] = None
    sizes: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    stock: Optional[int] = None
    image_urls: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_bestseller: Optional[bool] = None
    tags: Optional[List[str]] = None

class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    sale_price: Optional[float] = None
    sku: Optional[str] = None
    category: str
    sizes: List[str] = []
    colors: List[str] = []
    stock: int
    image_urls: List[str] = []
    is_featured: bool = False
    is_bestseller: bool = False
    tags: List[str] = []
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
