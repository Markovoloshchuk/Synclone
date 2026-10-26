from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Clone Memory Synchronizer"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/clone_db"

    class Config:
        env_file = ".env"


settings = Settings()
