from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import get_db as _get_db
from app.services.mock_scan_workflow import mock_scan_workflow
from app.services.ports import ScanWorkflowPort


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()


def get_scan_workflow() -> ScanWorkflowPort:
    """Swap mock for a Postgres-backed implementation when persistence is wired."""
    return mock_scan_workflow
