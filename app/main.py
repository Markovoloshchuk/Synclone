from fastapi import FastAPI

from app.core.database import Base, engine

# Створення таблиць у БД під час запуску
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Synclone API",
    description="Синхронізатор пам'яті для клонів (Data-Intensive Application)",
    version="0.1.0",
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
