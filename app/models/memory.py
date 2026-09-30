from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


class MemoryBackup(Base):
    __tablename__ = "memory_backups"

    id = Column(Integer, primary_key=True, index=True)
    clone_id = Column(String, index=True, nullable=False)
    memory_hash = Column(String, nullable=False)
    size_mb = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
