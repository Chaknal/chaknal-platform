from pydantic_settings import BaseSettings
from typing import List
import os
import json


class Settings(BaseSettings):
    # Database - Try to get from environment first, then from app-settings.json, then default to SQLite
    DATABASE_URL: str = "sqlite+aiosqlite:///./chaknal.db"

    # Security
    SECRET_KEY: str = ""  # Must be set via environment variable
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_ORIGINS: str = ""
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOW_HEADERS: List[str] = ["*"]

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chaknall Platform"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def cors_origins(self) -> List[str]:
        if self.is_production:
            # In production, use CORS_ORIGINS environment variable if set, otherwise use ALLOWED_ORIGINS
            if self.CORS_ORIGINS:
                return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
            return self.ALLOWED_ORIGINS
        else:
            # In development, allow common dev origins
            return ["*"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # If DATABASE_URL is not set in environment, try to load from app-settings.json
        if self.DATABASE_URL == "sqlite+aiosqlite:///./chaknal.db" and os.path.exists("app-settings.json"):
            try:
                with open("app-settings.json", "r") as f:
                    app_settings = json.load(f)
                for setting in app_settings:
                    if setting["name"] == "DATABASE_URL":
                        self.DATABASE_URL = setting["value"]
                        print(f"✅ Loaded PostgreSQL URL from app-settings.json")
                        break
            except Exception as e:
                print(f"⚠️ Could not load DATABASE_URL from app-settings.json: {e}")


settings = Settings()
