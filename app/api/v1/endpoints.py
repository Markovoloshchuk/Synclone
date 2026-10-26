from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.clone import CloneBackup
from app.schemas.clone import CloneBackupCreate, CloneBackupResponse

router = APIRouter(prefix="/api/v1/clones", tags=["Clone Memory Sync"])


@router.post(
    "/backups/", response_model=CloneBackupResponse, status_code=status.HTTP_201_CREATED
)
async def create_backup(backup_in: CloneBackupCreate, user: CurrentUser, db: DbSession):
    backup = CloneBackup(
        owner_id=user.id,
        clone_identifier=backup_in.clone_identifier.strip(),
        resident_name=backup_in.resident_name.strip(),
        memory_payload_hash=backup_in.memory_payload_hash.strip(),
        status="synced",
    )
    db.add(backup)
    await db.commit()
    await db.refresh(backup)
    return backup


@router.get("/backups/", response_model=list[CloneBackupResponse])
async def list_backups(user: CurrentUser, db: DbSession):
    result = await db.scalars(
        select(CloneBackup)
        .where(CloneBackup.owner_id == user.id)
        .order_by(CloneBackup.created_at.desc())
    )
    return list(result.all())


@router.get("/backups/{clone_identifier}", response_model=CloneBackupResponse)
async def get_backup(clone_identifier: str, user: CurrentUser, db: DbSession):
    result = await db.scalar(
        select(CloneBackup)
        .where(
            CloneBackup.owner_id == user.id,
            CloneBackup.clone_identifier == clone_identifier,
        )
        .order_by(CloneBackup.created_at.desc())
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Clone backup not found")
    return result
