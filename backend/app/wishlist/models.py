from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint, Column
from sqlalchemy.orm import relationship, Mapped
from datetime import datetime
from ..database import Base

class Favorite(Base):
    __tablename__ = 'wishlist'
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name = 'uq_favorite_user_product'),
    )

    id  = Column(Integer, primary_key = True)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship('User')
    product = relationship('Product')