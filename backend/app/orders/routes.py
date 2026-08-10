from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import User, get_current_user
from .schemas import OrderCreate, OrderResponse
from .service import OrderService

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate,
                 user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return OrderService(db).create(user.id, data.cart)


@router.get("", response_model=list[OrderResponse])
def my_orders(user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    return OrderService(db).list_for_user(user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int,
              user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    return OrderService(db).get_for_user(order_id, user.id)