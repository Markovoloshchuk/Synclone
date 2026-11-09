# app/schemas/user.py
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.USER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
