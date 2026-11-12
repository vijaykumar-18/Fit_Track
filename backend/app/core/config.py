from typing import Literal
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "FitTrack API"
    database_url: str = "sqlite:///./fittrack.db"
    secret_key: str = "replace-this-with-a-long-random-secret"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    reminder_hour: int = Field(default=9, ge=0, le=23)
    reminder_minute: int = Field(default=0, ge=0, le=59)
    reminder_timezone: str = "UTC"
    environment: Literal["development", "production"] = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def require_production_secret(self):
        if self.environment == "production" and (
            len(self.secret_key) < 32 or self.secret_key.startswith("replace-this")
        ):
            raise ValueError("Production SECRET_KEY must be a unique value of at least 32 characters")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def cors_origin_regex(self) -> str | None:
        if self.environment == "development":
            return r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"
        return None

settings = Settings()
