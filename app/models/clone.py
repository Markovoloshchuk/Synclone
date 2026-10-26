from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CloneBackup(Base):
    __tablename__ = "clone_backups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    clone_identifier: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    resident_name: Mapped[str] = mapped_column(String(150))
    memory_payload_hash: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, synced, corrupted
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
