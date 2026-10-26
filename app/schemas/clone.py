from datetime import datetime

from pydantic import BaseModel


class CloneBackupCreate(BaseModel):
    clone_identifier: str
    resident_name: str
    memory_payload_hash: str


class CloneBackupResponse(CloneBackupCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
