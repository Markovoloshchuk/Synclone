from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.endpoints import router as clone_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import hash_password
from app.models.user import User


async def initialize_database():
    # Simple bootstrap for this coursework project.
    # For production, replace with Alembic migrations.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        email = settings.INITIAL_ADMIN_EMAIL.lower().strip()
        existing = await db.scalar(select(User).where(User.email == email))
        if existing is None:
            if len(settings.INITIAL_ADMIN_PASSWORD) < 12:
                raise RuntimeError(
                    "INITIAL_ADMIN_PASSWORD must contain at least 12 characters"
                )
            db.add(
                User(
                    email=email,
                    full_name=settings.INITIAL_ADMIN_NAME,
                    password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                    role="admin",
                    is_active=True,
                )
            )
            await db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await initialize_database()
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="Synclone backup registry with role-based access control.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(clone_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Synclone API", "status": "active"}


@app.get("/health")
async def health():
    return {"status": "ok"}
