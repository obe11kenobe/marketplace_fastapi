from authx import TokenPayload
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status

from ...database import get_db
from ..models.user import User
from ..repositories.user import UserRepository
from ..schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
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

def get_current_user(
        payload: TokenPayload = Depends(security.access_token_required),
        db: Session = Depends(get_db),
) -> User:
    user = UserRepository(db).get_by_id(int(payload.sub))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь недоступен")
    return user