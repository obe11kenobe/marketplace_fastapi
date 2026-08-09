from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .category import CategoryResponse, CategoryBase


class ProductBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=100,
                      description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., description="Product price", gt = 0)
    category_id: int = Field(..., description="Product category id")
    image_url: Optional[str] = Field(None, description="Product image url")


class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int = Field(..., description="Unique product id")
    name: str
    description: Optional[str]
    price: float
    category_id: Optional[int]
    image_url: Optional[str]
    created_at: datetime
    category: CategoryResponse = Field(..., description="Product category details")

    class Config:
        from_attributes = True

class ProductListResponse(ProductBase):
    products: list[ProductResponse]
    total: int = Field(..., description="Total number of products")
