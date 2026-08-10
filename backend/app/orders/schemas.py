from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel

class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    cart: Dict[int, int]

class OrderResponse(BaseModel):
    id: int
    status: str
    total: float
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True