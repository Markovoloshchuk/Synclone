"""Бекапи свідомості: CRUD для власних записів + статистика (MVP)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.memory import MemoryBackup
from app.models.user import ROLE_ADMIN, User
from app.schemas import BackupCreate, BackupOut, BackupStats

router = APIRouter(prefix="/api/backups", tags=["backups"])


@router.get("", response_model=list[BackupOut])
def list_backups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MemoryBackup]:
    """Список ЛИШЕ власних бекапів (горизонтальний ізоляційний контроль)."""
    return list(
        db.scalars(
            select(MemoryBackup).where(MemoryBackup.user_id == current_user.id)
        ).all()
    )


@router.post(
    "",
    response_model=BackupOut,
    status_code=status.HTTP_201_CREATED,
)
def create_backup(
    payload: BackupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryBackup:
    """Створює бекап, прив'язаний до поточного користувача."""
    backup = MemoryBackup(**payload.model_dump(), user_id=current_user.id)
    db.add(backup)
    db.commit()
    db.refresh(backup)
    return backup


@router.get("/stats", response_model=BackupStats)
def backup_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BackupStats:
    """Агрегати власних бекапів: кількість та загальний обсяг."""
    count, total = db.execute(
        select(
            func.count(MemoryBackup.id),
            func.coalesce(func.sum(MemoryBackup.size_mb), 0),
        ).where(MemoryBackup.user_id == current_user.id)
    ).one()
    return BackupStats(count=count, total_size_mb=int(total))


@router.delete("/{backup_id}")
def delete_backup(
    backup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Видалення бекапа; чужий бекап (IDOR) → 403, не 404."""
    backup = db.get(MemoryBackup, backup_id)
    if backup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup not found",
        )
    if backup.user_id != current_user.id and current_user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete another user's backup",
        )
    db.delete(backup)
    db.commit()
    return {"detail": "deleted"}
