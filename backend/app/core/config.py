from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ESM Platform API"
    database_url: str = "sqlite:///./esm.db"
    jwt_secret: str = "development-only-secret-change-this-value-0123456789"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ESM_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
