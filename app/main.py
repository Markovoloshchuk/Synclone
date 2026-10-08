from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine

# Імпорт моделей реєструє їх у Base.metadata — без цього create_all
# не створить таблиці моделей.
from app.models import MemoryBackup  # noqa: F401

# Створення таблиць у БД під час запуску
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Синхронізатор пам'яті для клонів (Data-Intensive Application)",
    version=settings.app_version,
)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "Synclone Memory Sync",
        "message": "Система готовна до прийому бекапів свідомості",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
