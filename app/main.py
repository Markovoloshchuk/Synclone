from fastapi import FastAPI

from app.api.v1.endpoints import router as clone_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="High-load memory synchronization system for clones.",
)

app.include_router(clone_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Clone Memory Synchronizer API",
        "status": "active",
    }
