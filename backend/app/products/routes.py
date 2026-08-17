from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import User, require_seller
from .service import ProductService
from .schemas import ProductResponse, ProductListResponse, ProductCreate, ProductUpdate

router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)

@router.get('', response_model=ProductListResponse, status_code=status.HTTP_200_OK)
def get_products(db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_products()

@router.get('/my', response_model=ProductListResponse, status_code=status.HTTP_200_OK)
def get_my_products(seller: User = Depends(require_seller), db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_seller_products(seller.id)

@router.get('/{product_id}', response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_product(product_id)

@router.get("/category/{category_id}", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_products_by_category(category_id)

@router.post('', response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, seller: User = Depends(require_seller),
                   db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.create_product(data, seller.id)

@router.put('/{product_id}', response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(product_id: int, data: ProductUpdate, seller: User = Depends(require_seller),
                   db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.update_product(product_id, data, seller.id)

@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, seller: User = Depends(require_seller),
                   db: Session = Depends(get_db)):
    service = ProductService(db)
    service.delete_product(product_id, seller.id)
