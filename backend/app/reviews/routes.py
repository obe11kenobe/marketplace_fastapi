from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import User, get_current_user, require_admin
from ..auth.service.user_service import get_optional_user
from .schemas import ProductRatingResponse, ReviewCreate, ReviewModerate, ReviewResponse, ReviewUpdate
from .service import ReviewService

router = APIRouter(prefix="/api", tags=["reviews"])


@router.get("/products/{product_id}/reviews", response_model=list[ReviewResponse])
def product_reviews(product_id: int,
                    user: User | None = Depends(get_optional_user),
                    db: Session = Depends(get_db)):
    return ReviewService(db).list_for_product(product_id, user.id if user else None)


@router.get("/products/{product_id}/rating", response_model=ProductRatingResponse)
def product_rating(product_id: int, db: Session = Depends(get_db)):
    return ReviewService(db).rating_for_product(product_id)


@router.get("/reviews/moderation", response_model=list[ReviewResponse])
def moderation_queue(_: User = Depends(require_admin),
                     db: Session = Depends(get_db)):
    return ReviewService(db).list_pending()


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
def create_review(data: ReviewCreate,
                  user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    return ReviewService(db).create(user.id, data.product_id, data.rating, data.text)


@router.patch("/reviews/{review_id}", response_model=ReviewResponse)
def update_review(review_id: int,
                  data: ReviewUpdate,
                  user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    return ReviewService(db).update(review_id, user.id, data)


@router.patch("/reviews/{review_id}/status", response_model=ReviewResponse)
def moderate_review(review_id: int,
                    data: ReviewModerate,
                    _: User = Depends(require_admin),
                    db: Session = Depends(get_db)):
    return ReviewService(db).moderate(review_id, data.status)


@router.delete("/reviews/{review_id}", status_code=204)
def delete_review(review_id: int,
                  user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    ReviewService(db).delete(review_id, user)
