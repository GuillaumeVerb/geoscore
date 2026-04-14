"""Liveness / readiness endpoints (no scoring)."""

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def test_health_ok() -> None:
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_skips_db_when_mock_workflow() -> None:
    prev = settings.use_mock_workflow
    try:
        settings.use_mock_workflow = True
        r = TestClient(app).get("/ready")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ready"
        assert body["workflow"] == "mock"
        assert body["database"] == "skipped"
    finally:
        settings.use_mock_workflow = prev
