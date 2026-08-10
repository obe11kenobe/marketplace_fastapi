from datetime import timedelta

import bcrypt
from authx import AuthX, AuthXConfig

from ...config import settings

config = AuthXConfig(
    JWT_SECRET_KEY=settings.jwt_secret_key,
    JWT_TOKEN_LOCATION=["headers"],          # токен ищем в заголовке Authorization
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=settings.jwt_access_expires_minutes),
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=settings.jwt_refresh_expires_days),
)

security = AuthX(config=config)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())