from typing import Dict, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..products.repository import ProductRepository
from .models import Order, OrderItem
from .repository import OrderRepository
from .schemas import OrderResponse

class OrderService:
    def __init__(self, db: Session):
        self.orders = OrderRepository(db)
        self.products = ProductRepository(db)

    def create(self, user_id: int, cart: Dict[int, int]) -> OrderResponse:
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Корзина пуста",
            )

        products = {p.id: p for p in self.products.get_multiole_by_ids(list(cart))}

        items: List[OrderItem] = []
        total = 0.0

        for product_id, quantity in cart.items():
            product = products.get(product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Товар с id {product_id} не найден",
                )
            if quantity < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Некорректное количество для товара {product_id}",
                )

            items.append(OrderItem(product_id=product.id, quantity=quantity, price=product.price))
            total += product.price * quantity

        order = Order(user_id=user_id, total=round(total, 2), items=items)

        return OrderResponse.model_validate(self.orders.create(order))

    def list_for_user(self, user_id: int) -> List[OrderResponse]:
        return [OrderResponse.model_validate(o) for o in self.orders.list_for_user(user_id)]

    def get_for_user(self, order_id: int, user_id: int) -> OrderResponse:
        order = self.orders.get_owned(order_id, user_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден",
            )
        return OrderResponse.model_validate(order)
