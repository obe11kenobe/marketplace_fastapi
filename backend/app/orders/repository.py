from typing import List, Optional

from sqlalchemy.orm import Session

from .models import Order

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        return order

    def list_for_user(self, user_id: int) -> List[Order]:
        return (
            self.db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    def get_owned(self, order_id: int, user_id: int) -> Optional[Order]:
        return (
            self.db.query(Order)
            .filter(Order.id == order_id, Order.user_id == user_id)
            .first()
        )
