import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.endpoints import router as clone_router
from app.core.config import settings

logger = logging.getLogger(__name__)

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
