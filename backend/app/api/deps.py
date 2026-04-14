from __future__ import annotations

from collections.abc import Generator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
import jwt

from app.core.tokens import decode_access_token
from app.db.session import get_db as _get_db
from app.schemas.api_contracts import UserSummary
from app.services.mock_scan_workflow import mock_scan_workflow
from app.services.postgres_scan_workflow import postgres_scan_workflow
from app.services.ports import ScanWorkflowPort

_bearer = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> UserSummary:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_access_token(creds.credentials)
        uid = UUID(str(payload["sub"]))
        email = str(payload.get("email") or "")
        return UserSummary(id=uid, email=email)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        ) from exc
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        ) from exc


def get_scan_workflow() -> ScanWorkflowPort:
    """Use mock for local UI-only runs; default is Postgres-backed pipeline."""
    if settings.use_mock_workflow:
        return mock_scan_workflow
    return postgres_scan_workflow
