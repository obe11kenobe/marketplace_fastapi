from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..auth import User
from ..orders.repository import OrderRepository
from ..products.repository import ProductRepository
from .models import Review, REVIEW_TRANSITIONS
from .repository import ReviewRepository
from .schemas import ProductRatingResponse, ReviewResponse, ReviewUpdate


def can_transition(current: str, new: str) -> bool:
    return new in REVIEW_TRANSITIONS.get(current, set())


class ReviewService:
    def __init__(self, db: Session):
        self.reviews = ReviewRepository(db)
        self.products = ProductRepository(db)
        self.orders = OrderRepository(db)

    def list_for_product(self, product_id: int, user_id: int | None = None) -> list[ReviewResponse]:
        reviews = self.reviews.list_approved_reviews(product_id)

        if user_id is not None:
            own = self.reviews.get_by_user_and_product(user_id, product_id)
            if own and own.status != 'approved':
                reviews = [own, *reviews]

        return [ReviewResponse.model_validate(r) for r in reviews]

    def rating_for_product(self, product_id: int) -> ProductRatingResponse:
        average, count = self.reviews.rating_for_product(product_id)

        return ProductRatingResponse(
            product_id=product_id,
            average_rating=round(average, 2) if average is not None else None,
            count=count,
        )

    def create(self, user_id: int, product_id: int, rating: int, text: str | None) -> ReviewResponse:
        if not self.products.get_by_id(product_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не найден",
            )

        if not self.orders.user_bought_product(user_id, product_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Отзыв можно оставить только на купленный товар",
            )

        if self.reviews.get_by_user_and_product(user_id, product_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Вы уже оставляли отзыв на этот товар",
            )

        review = Review(user_id=user_id, product_id=product_id, rating=rating, text=text)

        return ReviewResponse.model_validate(self.reviews.create_review(review))

    def update(self, review_id: int, user_id: int, data: ReviewUpdate) -> ReviewResponse:
        review = self._get_own(review_id, user_id)

        changes = data.model_dump(exclude_unset=True)
        if not changes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нечего менять",
            )

        for field, value in changes.items():
            setattr(review, field, value)

        review.status = 'pending'

        return ReviewResponse.model_validate(self.reviews.save_review(review))

    def delete(self, review_id: int, user: User) -> None:
        review = self.reviews.get_review(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отзыв не найден",
            )

        if review.user_id != user.id and user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Можно удалить только свой отзыв",
            )

        self.reviews.delete_review(review)

    def list_pending(self) -> list[ReviewResponse]:
        return [ReviewResponse.model_validate(r) for r in self.reviews.list_pending_reviews()]

    def moderate(self, review_id: int, new_status: str) -> ReviewResponse:
        review = self.reviews.get_review(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отзыв не найден",
            )

        if not can_transition(review.status, new_status):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Нельзя перевести отзыв из «{review.status}» в «{new_status}»",
            )

        review.status = new_status

        return ReviewResponse.model_validate(self.reviews.save_review(review))

    def _get_own(self, review_id: int, user_id: int) -> Review:
        review = self.reviews.get_review(review_id)
        if not review or review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отзыв не найден",
            )
        return review
