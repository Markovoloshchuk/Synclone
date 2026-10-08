"""Налаштування застосунку Synclone."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Налаштування, що завантажуються з .env або змінних середовища."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Synclone API"
    app_version: str = "0.1.0"

    # URL реляційної бази даних: за замовчуванням — локальний SQLite
    # для швидкого старту; у проді перевизначається змінною DATABASE_URL
    # (PostgreSQL) через файл .env.
    database_url: str = "sqlite:///./synclone.db"

    debug: bool = True


settings = Settings()
