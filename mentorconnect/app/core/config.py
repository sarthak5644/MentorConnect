"""
app/core/config.py
-------------------
Centralized application configuration loaded from environment variables (.env).
Uses pydantic-settings so every value is validated and type-checked at startup,
which means the app fails fast (instead of at runtime) if config is missing/wrong.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    # ---------------- App ----------------
    APP_NAME: str = "MentorConnect"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # ---------------- Database ----------------
    DB_HOST: str = "db"
    DB_PORT: int = 3306
    DB_USER: str = "mentorconnect_user"
    DB_PASSWORD: str = "change_this_password"
    DB_NAME: str = "mentorconnect_db"
    DB_ROOT_PASSWORD: str = "change_this_root_password"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 1800

    # ---------------- JWT ----------------
    JWT_SECRET_KEY: str = "insecure-dev-secret-change-me"
    JWT_REFRESH_SECRET_KEY: str = "insecure-dev-refresh-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---------------- Security ----------------
    BCRYPT_ROUNDS: int = 12
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    CSRF_SECRET_KEY: str = "insecure-csrf-secret-change-me"

    # ---------------- OTP ----------------
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60

    # ---------------- Captcha ----------------
    CAPTCHA_LENGTH: int = 6
    CAPTCHA_EXPIRE_MINUTES: int = 5
    CAPTCHA_WIDTH: int = 220
    CAPTCHA_HEIGHT: int = 90

    # ---------------- Email ----------------
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "no-reply@mentorconnect.com"
    SMTP_FROM_NAME: str = "MentorConnect"
    SMTP_USE_TLS: bool = True

    # ---------------- SMS ----------------
    SMS_PROVIDER: str = "console"
    SMS_API_KEY: str = ""
    SMS_API_SECRET: str = ""
    SMS_SENDER_ID: str = "MENTORC"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""

    # ---------------- File Upload ----------------
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]
    ALLOWED_DOCUMENT_EXTENSIONS: List[str] = ["pdf", "jpg", "jpeg", "png"]

    # ---------------- Rate Limiting ----------------
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_OTP: str = "3/minute"

    # ---------------- Logging ----------------
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    LOG_RETENTION_DAYS: int = 30

    # ---------------- Super Admin Bootstrap ----------------
    SUPERADMIN_EMAIL: str = "admin@mentorconnect.com"
    SUPERADMIN_PASSWORD: str = "ChangeMe@123"
    SUPERADMIN_FULL_NAME: str = "Super Admin"

    @field_validator("BACKEND_CORS_ORIGINS", "ALLOWED_IMAGE_EXTENSIONS", "ALLOWED_DOCUMENT_EXTENSIONS", mode="before")
    @classmethod
    def parse_list_from_str(cls, v):
        """Allow comma separated or JSON-style list strings from .env files."""
        if isinstance(v, str) and not v.startswith("["):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Build the MySQL connection string for SQLAlchemy using PyMySQL driver."""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Singleton settings instance imported across the app
settings = Settings()
