from typing import List

from authx import TokenPayload
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status

from ...database import get_db
from ..models.user import User
from ..repositories.user import UserRepository
from ..schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, RoleUpdate
from ..security.security import security, hash_password, verify_password

class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def register(self, data: UserCreate) -> UserResponse:
        if self.users.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует",
            )
        user = self.users.create(data.email, hash_password(data.password))
        return UserResponse.model_validate(user)

    def login(self, data: UserLogin) -> TokenResponse:
        user = self.users.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Неверный email или пароль'
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Аккаунт заблокирован'
            )

        return TokenResponse(
            access_token=security.create_access_token(uid=str(user.id)),
            refresh_token=security.create_refresh_token(uid=str(user.id)),
        )

    def list_users(self) -> List[UserResponse]:
        return [UserResponse.model_validate(u) for u in self.users.list_all()]

    def set_role(self, user_id: int, data: RoleUpdate, actor: User) -> UserResponse:
        if user_id == actor.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя менять роль самому себе",
            )

        user = self.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        user.role = data.role
        return UserResponse.model_validate(self.users.save(user))

def get_current_user(
        payload: TokenPayload = Depends(security.access_token_required),
        db: Session = Depends(get_db),
) -> User:
    user = UserRepository(db).get_by_id(int(payload.sub))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь недоступен")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только администраторам",
        )
    return user

def require_seller(user: User = Depends(get_current_user)) -> User:
    if user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только продавцам",
        )
    return user
