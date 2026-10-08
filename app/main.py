"""Точка входу Synclone: API-роутери, сід адмініста, статичні сторінки."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import MemoryBackup, User  # noqa: F401  реєстрація моделей
from app.models.user import ROLE_ADMIN
from app.routers import admin, auth, backups, users

# Створення таблиць у БД під час запуску
Base.metadata.create_all(bind=engine)


def ensure_admin() -> None:
    """Сідить адміністратора з .env — публічної реєстрації адмінів немає."""
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == settings.admin_email))
        if existing is None:
            db.add(
                User(
                    email=settings.admin_email,
                    hashed_password=hash_password(settings.admin_password),
                    role=ROLE_ADMIN,
                )
            )
            db.commit()
    finally:
        db.close()


ensure_admin()

app = FastAPI(
    title=settings.app_name,
    description="Синхронізатор пам'яті для клонів (Data-Intensive Application)",
    version=settings.app_version,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(backups.router)
app.include_router(admin.router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy"}


# Статичні сторінки-заглушки; підключається ОСТАННІМ,
# щоб API-маршрути мали пріоритет над catch-all "/"
static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
