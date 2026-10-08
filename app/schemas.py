"""Pydantic-схеми запитів та відповідей API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email: str | None = Field(default=None, min_length=3, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class AdminUserUpdate(BaseModel):
    is_active: bool


class BackupCreate(BaseModel):
    clone_id: str = Field(min_length=1, max_length=100)
    memory_hash: str = Field(min_length=8, max_length=128)
    size_mb: int = Field(gt=0, le=1_000_000)


class BackupOut(BaseModel):
    id: int
    user_id: int
    clone_id: str
    memory_hash: str
    size_mb: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BackupStats(BaseModel):
    count: int
    total_size_mb: int
