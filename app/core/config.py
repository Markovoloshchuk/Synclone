from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Synclone"
    DATABASE_URL: str = (
        "postgresql+asyncpg://synclone:change-this-db-password@localhost:5432/synclone"
    )
    JWT_SECRET_KEY: str = "unsafe-development-secret-change-me"
    JWT_EXPIRE_MINUTES: int = 60
    INITIAL_ADMIN_EMAIL: str = "admin@example.com"
    INITIAL_ADMIN_PASSWORD: str = "change-this-admin-password"
    INITIAL_ADMIN_NAME: str = "Synclone Administrator"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]


settings = Settings()
