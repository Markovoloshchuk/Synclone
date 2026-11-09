import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.endpoints import router as clone_router
from app.core.config import settings
from app.core.database import (
    AsyncSessionLocal,
    Base,
    engine,
)
from app.core.security import get_password_hash

# <-- Додали AsyncSessionLocal
# ВАЖЛИВО: імпортуємо модель User та UserRole
from app.models.user import User, UserRole  # <-- Додали UserRole

logger = logging.getLogger(__name__)


# Визначаємо lifecycle-події (startup / shutdown) за допомогою lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Створення таблиць
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully.")

    # 2. Автоматичне створення початкового адміністратора з .env
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == settings.INITIAL_ADMIN_EMAIL)
        )
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            logger.info("Initial admin not found. Creating default admin...")
            new_admin = User(
                email=settings.INITIAL_ADMIN_EMAIL,
                full_name=settings.INITIAL_ADMIN_NAME,
                password_hash=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(new_admin)
            await session.commit()
            logger.info(
                f"Default admin created successfully ({settings.INITIAL_ADMIN_EMAIL})."
            )
        else:
            logger.info("Initial admin already exists.")

    yield
    pass


is_sandbox = settings.APP_ENV == "sandbox"

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="High-load memory synchronization system for clones.",
    debug=settings.DEBUG,
    docs_url="/docs" if is_sandbox else None,
    redoc_url="/redoc" if is_sandbox else None,
    openapi_url="/openapi.json" if is_sandbox else None,
    lifespan=lifespan,  # Підключаємо наш lifespan сюди
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(clone_router)
# app.include_router(home_router)


@app.exception_handler(Exception)
async def internal_server_error_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled error: %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


@app.get("/")
async def root():
    return {
        "message": "Welcome to Clone Memory Synchronizer API",
        "status": "active",
    }
