from typing import List

from authx import TokenPayload
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, RoleUpdate
from ..security.security import security, login_rate_limit
from ..service.user_service import AuthService, get_current_user, require_admin

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return AuthService(db).register(data)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(login_rate_limit)])
def login(data: UserLogin, db: Session = Depends(get_db)):
    return AuthService(db).login(data)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/users", response_model=List[UserResponse])
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return AuthService(db).list_users()

@router.patch("/users/{user_id}/role", response_model=UserResponse)
def set_user_role(user_id: int, data: RoleUpdate,
                  admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return AuthService(db).set_role(user_id, data, admin)

@router.post("/refresh")
def refresh(payload: TokenPayload = Depends(security.refresh_token_required)):
    return {"access_token": security.create_access_token(uid=payload.sub)}