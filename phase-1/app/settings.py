from functools import lru_cache

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.exceptions import SettingsError


class AppSettings(BaseSettings):
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY", min_length=20)
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL", min_length=1)
    openai_timeout_seconds: int = Field(default=30, alias="OPENAI_TIMEOUT_SECONDS", ge=5, le=300)
    openai_max_retries: int = Field(default=2, alias="OPENAI_MAX_RETRIES", ge=0, le=10)
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    try:
        return AppSettings()
    except ValidationError as exc:
        raise SettingsError(f"Invalid application settings: {exc}") from exc
