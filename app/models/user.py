"""Модель користувача системи."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.core.database import Base

ROLE_ADMIN = "admin"
ROLE_USER = "user"


class User(Base):
    """Користувач Synclone; роль визначає вертикальний доступ (403)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(16), nullable=False, default=ROLE_USER)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
