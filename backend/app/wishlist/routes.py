from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import User, get_current_user
from .schemas import WishlistCreate, WishlistProductResponse
from .service import WishlistService

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])


@router.get("", response_model=list[WishlistProductResponse])
def my_wishlist(user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return WishlistService(db).list_for_user(user.id)


@router.post("", response_model=WishlistProductResponse, status_code=201)
def add_to_wishlist(data: WishlistCreate,
                    user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    return WishlistService(db).add_wishlist(user.id, data.product_id)


@router.delete("/{product_id}", status_code=204)
def remove_from_wishlist(product_id: int,
                         user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    WishlistService(db).remove_wishlist(user.id, product_id)
