import os
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Визначаємо середовище, для якого потрібно прочитати конфігурацію.
CURRENT_ENV = os.getenv("APP_ENV", "sandbox")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f".env.{CURRENT_ENV}",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: Literal["sandbox", "production"] = "sandbox"
    PROJECT_NAME: str = "Clone Memory Synchronizer"
    DATABASE_URL: str
    DEBUG: bool = False
    JWT_SECRET_KEY: str
    JWT_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Початковий адміністратор створюється одноразово окремим bootstrap-кроком.
    INITIAL_ADMIN_EMAIL: str | None = None
    INITIAL_ADMIN_PASSWORD: str | None = None
    INITIAL_ADMIN_NAME: str | None = None

    @model_validator(mode="after")
    def validate_runtime_settings(self):
        if self.APP_ENV == "production" and self.DEBUG:
            raise ValueError("DEBUG must be False in Production environment")

        admin_values = (
            self.INITIAL_ADMIN_EMAIL,
            self.INITIAL_ADMIN_PASSWORD,
            self.INITIAL_ADMIN_NAME,
        )
        if any(admin_values) and not all(admin_values):
            raise ValueError(
                "INITIAL_ADMIN_EMAIL, INITIAL_ADMIN_PASSWORD and "
                "INITIAL_ADMIN_NAME must be set together"
            )
        if self.INITIAL_ADMIN_PASSWORD and len(self.INITIAL_ADMIN_PASSWORD) < 8:
            raise ValueError("INITIAL_ADMIN_PASSWORD must be at least 8 characters")

        return self


settings = Settings()
