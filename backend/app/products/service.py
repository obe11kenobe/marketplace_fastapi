from sqlalchemy.orm import Session
from typing import List

from .models import Product
from .repository import ProductRepository
from ..categories.repository import CategoryRepository
from .schemas import ProductResponse, ProductListResponse, ProductCreate, ProductUpdate
from fastapi import HTTPException, status


class ProductService:
    def __init__(self,db: Session):
        self.product_repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)

    def get_products(self) -> ProductListResponse:
        products = self.product_repository.get_all()
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products_response))

    def get_product(self, product_id : int) -> ProductResponse:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
        return ProductResponse.model_validate(product)

    def get_products_by_category(self, category_id: int) -> ProductListResponse:
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )
        products = self.product_repository.get_by_category(category_id)
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products_response))

    def create_product(self, product_data: ProductCreate, seller_id: int) -> ProductResponse:
        self._check_category(product_data.category_id)
        product = self.product_repository.create(product_data, seller_id)
        return ProductResponse.model_validate(product)

    def get_seller_products(self, seller_id: int) -> ProductListResponse:
        products = self.product_repository.list_for_seller(seller_id)
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products_response))

    def update_product(self, product_id: int, data: ProductUpdate, seller_id: int) -> ProductResponse:
        product = self._get_owned(product_id, seller_id)

        changes = data.model_dump(exclude_unset=True)
        if "category_id" in changes:
            self._check_category(changes["category_id"])

        for field, value in changes.items():
            setattr(product, field, value)

        return ProductResponse.model_validate(self.product_repository.save(product))

    def delete_product(self, product_id: int, seller_id: int) -> None:
        self.product_repository.delete(self._get_owned(product_id, seller_id))

    def _get_owned(self, product_id: int, seller_id: int) -> Product:
        product = self.product_repository.get_owned(product_id, seller_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
        return product

    def _check_category(self, category_id: int) -> None:
        if not self.category_repository.get_by_id(category_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )