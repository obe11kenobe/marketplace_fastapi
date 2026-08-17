from sqlalchemy.orm import Session, joinedload
from typing import List
from ..products.models import Product
from .models import Favorite

class WishlistRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_favorite(self, wishlist: Favorite) -> Favorite:
        self.db.add(wishlist)
        self.db.commit()
        self.db.refresh(wishlist)

        return wishlist

    def list_for_user(self, user_id: int)  -> List[Favorite]:
        return (
            self.db.query(Favorite)
            .options(joinedload(Favorite.product).joinedload(Product.category))
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .all()
        )

    def get(self, user_id: int, product_id: int) -> Favorite | None:
        return (
            self.db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.product_id == product_id)
            .first()
        )

    def delete_favorite(self, wishlist: Favorite) -> Favorite | None:
        self.db.delete(wishlist)
        self.db.commit()