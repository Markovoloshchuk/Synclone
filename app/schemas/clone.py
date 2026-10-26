from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CloneBackupCreate(BaseModel):
    clone_identifier: str = Field(min_length=1, max_length=100)
    resident_name: str = Field(min_length=1, max_length=150)
    memory_payload_hash: str = Field(min_length=1, max_length=255)


class CloneBackupResponse(BaseModel):
    id: int
    owner_id: int
    clone_identifier: str
    resident_name: str
    memory_payload_hash: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
