from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db as _get_db
from app.services.mock_scan_workflow import mock_scan_workflow
from app.services.postgres_scan_workflow import postgres_scan_workflow
from app.services.ports import ScanWorkflowPort


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()


def get_scan_workflow() -> ScanWorkflowPort:
    """Use mock for local UI-only runs; default is Postgres-backed pipeline."""
    if settings.use_mock_workflow:
        return mock_scan_workflow
    return postgres_scan_workflow
