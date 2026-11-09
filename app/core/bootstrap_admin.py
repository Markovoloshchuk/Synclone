"""Create the configured initial administrator once, without changing existing users."""

import asyncio

from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User


async def bootstrap_admin() -> None:
    if not settings.INITIAL_ADMIN_EMAIL:
        print("Initial administrator bootstrap skipped (not configured).")
        return

    email = settings.INITIAL_ADMIN_EMAIL.strip().lower()
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(User).where(User.email == email))
        if existing is not None:
            print(
                "Initial administrator bootstrap skipped: "
                "an account with this email already exists."
            )
            return

        admin = User(
            email=email,
            full_name=settings.INITIAL_ADMIN_NAME.strip(),
            password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print("Initial administrator account created.")


if __name__ == "__main__":
    asyncio.run(bootstrap_admin())
