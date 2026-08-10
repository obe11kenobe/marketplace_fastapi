from pydantic_settings import BaseSettings
from typing import List, Union

class Settings(BaseSettings):
    app_name: str = "FastAPI Shop"
    debug: bool = True
    database_url: str = "sqlite:///./shop.db"
    cors_origins: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    static_dir: str = "static"
    images_dir: str = "static/images"
    jwt_secret_key: str
    jwt_access_expires_minutes: int = 15
    jwt_refresh_expires_days: int = 20

    class Config:
        env_file = ".env"

settings = Settings()