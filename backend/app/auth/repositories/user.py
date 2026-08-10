from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def list_all(self) -> List[User]:
        return self.db.query(User).order_by(User.created_at.desc()).all()

    def save(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def create(self, email: str, hashed_password: str, role: str = "user") -> User:
        user = User(email=email, hashed_password=hashed_password, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user
