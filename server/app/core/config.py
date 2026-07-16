from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SkillForge API"
    app_version: str = "0.1.0"
    app_environment: str = "development"
    app_debug: bool = True

    api_v1_prefix: str = "/api/v1"

    log_level: str = "INFO"

    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/skillforge",
        repr=False,
    )
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30

    jwt_secret_key: str = Field(
        default="development-secret-change-me-123456",
        min_length=32,
        repr=False,
    )
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "skillforge-api"
    jwt_audience: str = "skillforge-client"

    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
    )
    refresh_token_expire_days: int = Field(
        default=7,
        ge=1,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use the postgresql+asyncpg driver.")

        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("JWT_SECRET_KEY must contain at least 32 characters.")

        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
