from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class CloneBackup(Base):
    __tablename__ = "clone_backups"
    __table_args__ = (
        Index("ix_clone_backups_owner_clone", "owner_id", "clone_identifier"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    clone_identifier: Mapped[str] = mapped_column(
        String(100), index=True, nullable=False
    )
    resident_name: Mapped[str] = mapped_column(String(150), nullable=False)
    memory_payload_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    owner = relationship("User", back_populates="backups")
