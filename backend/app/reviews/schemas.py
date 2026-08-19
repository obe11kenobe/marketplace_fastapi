from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5, description='Review rating')
    text: str | None = Field(None, max_length=2000, description='Review text')


class ReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    text: str | None = Field(None, max_length=2000)

class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    text: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewModerate(BaseModel):
    status: Literal['approved', 'rejected']

class ProductRatingResponse(BaseModel):
    product_id: int
    average_rating: float | None
    count: int