from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _connect_args(url: str) -> dict:
    """Avoid hanging forever on bad DB hosts (e.g. Railway without linked Postgres)."""
    u = url.lower()
    if u.startswith("postgresql://") or u.startswith("postgresql+psycopg2://"):
        return {"connect_timeout": 15}
    return {}


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=_connect_args(settings.database_url),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
