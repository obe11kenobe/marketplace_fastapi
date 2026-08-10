from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..models.product import Product
from ..schemas.products import ProductCreate

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Product]:
        return self.db.query(Product).options(joinedload(Product.category)).all()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_category(self, category_id: int) -> Product:
        return self.db.query(Product).options(joinedload(Product.category)).filter(Product.category_id == category_id).all()

    def create(self, product_data: ProductCreate, seller_id: int) -> Product:
        product_db = Product(**product_data.model_dump(), seller_id=seller_id)
        self.db.add(product_db)
        self.db.commit()
        self.db.refresh(product_db)
        return product_db

    def get_owned(self, product_id: int, seller_id: int) -> Optional[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.id == product_id, Product.seller_id == seller_id)
            .first()
        )

    def list_for_seller(self, seller_id: int) -> List[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.seller_id == seller_id)
            .order_by(Product.created_at.desc())
            .all()
        )

    def save(self, product: Product) -> Product:
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()

    def get_multiole_by_ids(self, product_ids: List[int]) -> List[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.id.in_(product_ids))
            .all()
        )