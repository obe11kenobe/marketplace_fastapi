from sqlalchemy import func
from sqlalchemy.orm import Session
from .models import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def rating_for_product(self, product_id: int) -> tuple[float | None, int]:
        return (
            self.db.query(func.avg(Review.rating), func.count(Review.id))
            .filter(Review.product_id == product_id, Review.status == 'approved')
            .one()
        )

    def create_review(self, review: Review) -> Review:
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def save_review(self, review: Review) -> Review:
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete_review(self, review: Review) -> None:
        self.db.delete(review)
        self.db.commit()

    def get_review(self, review_id: int) -> Review | None:
        return self.db.get(Review, review_id)

    def get_by_user_and_product(self, user_id: int, product_id: int) -> Review | None:
        return (
            self.db.query(Review)
            .filter(Review.user_id == user_id, Review.product_id == product_id)
            .first()
        )

    def list_approved_reviews(self, product_id: int) -> list[Review]:
        return (
            self.db.query(Review)
            .filter(Review.product_id == product_id, Review.status == 'approved')
            .order_by(Review.created_at.desc())
            .all()
        )

    def list_pending_reviews(self) -> list[Review]:
      return (
          self.db.query(Review)
          .filter(Review.status == 'pending')
          .order_by(Review.created_at.asc())
          .all()
      )
