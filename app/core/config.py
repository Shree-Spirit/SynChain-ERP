from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    APP_NAME: str = "SynChain-ERP"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql://synchain:synchain@localhost:5432/synchain_erp"

    SECRET_KEY: str = "change-me-to-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    API_KEY: str = "synchain-erp-dev-api-key"

    CORS_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5173,http://localhost:8000,http://127.0.0.1:8000"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.CORS_ORIGINS.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
