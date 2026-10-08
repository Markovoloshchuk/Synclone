"""Адмін-панель API: кожен маршрут закритий роллю admin (інакше 403)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.memory import MemoryBackup
from app.models.user import User
from app.schemas import AdminUserUpdate, BackupOut, UserOut

# Захист на РІВНІ роутера: вертикальне розмежування прав (403)
router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_role("admin"))],
)


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    """Список усіх користувачів системи."""
    return list(db.scalars(select(User)).all())


@router.patch("/users/{user_id}", response_model=UserOut)
def set_user_active(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
) -> User:
    """Активація/деактивація користувача."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user


@router.get("/backups", response_model=list[BackupOut])
def list_all_backups(db: Session = Depends(get_db)) -> list[MemoryBackup]:
    """Усі бекапи системи (огляд адміністратора)."""
    return list(db.scalars(select(MemoryBackup)).all())


@router.get("/stats")
def system_stats(db: Session = Depends(get_db)) -> dict:
    """Агрегати системи: користувачі, бекапи, загальний обсяг."""
    users = db.scalar(select(func.count(User.id))) or 0
    backups, total = db.execute(
        select(
            func.count(MemoryBackup.id),
            func.coalesce(func.sum(MemoryBackup.size_mb), 0),
        )
    ).one()
    return {"users": users, "backups": backups, "total_size_mb": int(total)}
