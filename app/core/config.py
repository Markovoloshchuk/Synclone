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

    # --- Додаємо ці поля, і Pydantic сам візьме їх із .env файлу ---
    INITIAL_ADMIN_EMAIL: str
    INITIAL_ADMIN_PASSWORD: str
    INITIAL_ADMIN_NAME: str
    # -------------------------------------------------------------

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.APP_ENV == "production" and self.DEBUG:
            raise ValueError("DEBUG must be False in Production environment")
        return self


settings = Settings()
