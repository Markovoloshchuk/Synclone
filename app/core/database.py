from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """
    Initialize the database and create all missing tables.

    Importing the models registers their tables in SQLAlchemy metadata.
    """

    from app.models.clone import CloneBackup  # noqa: F401
    from app.models.user import User  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def ensure_initial_admin() -> None:
    """
    Create the initial administrator if it does not exist.
    """

    from sqlalchemy import select

    from app.core.security import get_password_hash
    from app.models.user import User, UserRole

    email = settings.INITIAL_ADMIN_EMAIL.strip().lower()

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        admin = result.scalar_one_or_none()

        if admin is None:
            admin = User(
                email=email,
                full_name=settings.INITIAL_ADMIN_NAME,
                password_hash=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
                role=UserRole.ADMIN.value,
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            return

        # Якщо цей email уже є в БД, гарантуємо роль адміністратора.
        if admin.role != UserRole.ADMIN.value:
            admin.role = UserRole.ADMIN.value
            await session.commit()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
