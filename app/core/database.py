from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# URL реляційної БД задається через конфіг (.env / змінні середовища).
# За замовчуванням — локальний SQLite; у проді перемикається на PostgreSQL.
engine = create_engine(
    settings.database_url,
    connect_args=(
        {"check_same_thread": False}
        if settings.database_url.startswith("sqlite")
        else {}
    ),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Залежність FastAPI: сесія БД для одного запиту."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
