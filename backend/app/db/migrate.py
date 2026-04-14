"""Apply Alembic migrations (Postgres workflow only)."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import settings

_BACKEND_ROOT = Path(__file__).resolve().parents[2]


def run_alembic_upgrade_to_head() -> None:
    """Run ``alembic upgrade head`` programmatically (same as CLI from ``backend/``)."""
    ini = _BACKEND_ROOT / "alembic.ini"
    cfg = Config(str(ini))
    cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(cfg, "head")
