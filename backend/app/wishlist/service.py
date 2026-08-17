from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
from ..products.repository import ProductRepository
from .models import Favorite
from .repository import WishlistRepository
from .schemas import WishlistProductResponse

class WishlistService:
    def __init__(self, db: Session):
        self.wishlist = WishlistRepository(db)
        self.products = ProductRepository(db)

    def list_for_user(self, user_id: int) -> List[WishlistProductResponse]:
        return [WishlistProductResponse.model_validate(f) for f in self.wishlist.list_for_user(user_id)]

    def add_wishlist(self, user_id: int, product_id: int) -> WishlistProductResponse:
        wishlist_product = self.products.get_by_id(product_id)
        if not wishlist_product:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Продукт не найден"
            )
        existing = self.wishlist.get(user_id, product_id)
        if existing:
            return  WishlistProductResponse.model_validate(existing)

        favorite = Favorite(user_id = user_id, product_id = product_id)
        return WishlistProductResponse.model_validate(self.wishlist.create_favorite(favorite))

    def remove_wishlist(self, user_id: int, product_id: int) -> None:
        favorite = self.wishlist.get(user_id, product_id)
        if not favorite:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail='Товара нет в избранном'
            )
        self.wishlist.delete_favorite(favorite)
