from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..models.product import Product
from ..schemas.product import ProductCreate

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Product]:
        return self.db.query(Product).options(joinedload(Product.category)).all()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_category(self, category_id: int) -> Product:
        return self.db.query(Product).options(joinedload(Product.category)).filter(Product.category_id == category_id).all()

    def create(self, product_data: ProductCreate) -> Product:
        product_db =  Product(**product_data.model_dump())
        self.db.abb(product_db)
        self.db.commit()
        self.db.refresh(product_db)
        return product_db

    def get_multiole_by_ids(self, product_ids: List[int]) -> List[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.id.in_(product_ids))
            .all()
        )