import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.endpoints import router as clone_router
from app.core.config import settings
from app.core.database import engine, ensure_initial_admin, init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.

    On startup:
        Initialize the database and create missing tables.

    On shutdown:
        Dispose the SQLAlchemy engine.
    """

    try:
        await init_db()
        logger.info("Database initialized successfully")

        await ensure_initial_admin()
        logger.info("Initial administrator check completed")

        yield

    finally:
        await engine.dispose()
        logger.info("Database connections closed")


# Документація доступна лише в Sandbox.
is_sandbox = settings.APP_ENV == "sandbox"

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="High-load memory synchronization system for clones.",
    debug=settings.DEBUG,
    docs_url="/docs" if is_sandbox else None,
    redoc_url="/redoc" if is_sandbox else None,
    openapi_url="/openapi.json" if is_sandbox else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(clone_router)


# Обробка неочікуваних помилок сервера.
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
