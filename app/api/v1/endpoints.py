from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.clone import CloneBackup
from app.schemas.clone import CloneBackupCreate, CloneBackupResponse

router = APIRouter(prefix="/api/v1/clones", tags=["Clone Memory Sync"])


@router.post("/backups/", response_model=CloneBackupResponse)
async def create_backup(
    backup_in: CloneBackupCreate, db: AsyncSession = Depends(get_db)
):
    new_backup = CloneBackup(
        clone_identifier=backup_in.clone_identifier,
        resident_name=backup_in.resident_name,
        memory_payload_hash=backup_in.memory_payload_hash,
        status="synced",
    )
    db.add(new_backup)
    await db.commit()
    await db.refresh(new_backup)
    return new_backup


@router.get("/backups/{clone_identifier}", response_model=CloneBackupResponse)
async def get_backup(clone_identifier: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CloneBackup).filter(CloneBackup.clone_identifier == clone_identifier)
    )
    backup = result.scalars().first()
    if not backup:
        raise HTTPException(status_code=404, detail="Clone backup not found")
    return backup
