from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from ..database import Base

REVIEW_TRANSITIONS = {
    'pending': {'approved', 'rejected'},
    'approved': {'rejected'},
    'rejected': {'approved'},
}

class Review(Base):
    __tablename__ = 'reviews'
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uq_review_user_product'),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    text = Column(Text, nullable=True)
    status = Column(String, nullable=False, default='pending')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)