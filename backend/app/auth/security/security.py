import time
from collections import defaultdict
from datetime import timedelta

import bcrypt
from authx import AuthX, AuthXConfig
from fastapi import HTTPException, Request, status

from ...config import settings

config = AuthXConfig(
    JWT_SECRET_KEY=settings.jwt_secret_key,
    JWT_TOKEN_LOCATION=["headers"],
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=settings.jwt_access_expires_minutes),
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=settings.jwt_refresh_expires_days),
)

security = AuthX(config=config)

_attempts: dict[str, list[float]] = defaultdict(list)

def login_rate_limit(request: Request, max_attempts: int = 5, window: int = 60) -> None:
    """Не больше max_attempts попыток входа с одного IP за window секунд."""
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()

    recent = [t for t in _attempts[ip] if now - t < window]
    if len(recent) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком много попыток входа. Попробуйте через минуту.",
        )

    recent.append(now)
    _attempts[ip] = recent

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
