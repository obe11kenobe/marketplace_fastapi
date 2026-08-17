from datetime import datetime
from pydantic import BaseModel
from ..products.schemas import ProductResponse


class WishlistCreate(BaseModel):
    product_id: int

class WishlistResponse(BaseModel):
    id: int
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class WishlistProductResponse(BaseModel):
    id: int
    product_id: int
    created_at: datetime
    product: ProductResponse

    class Config:
        from_attributes = True