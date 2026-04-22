from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services.scan_create_rate_limit import check_scan_create_rate_limit, reset_scan_create_rate_limit_state


def test_rate_limit_allows_up_to_n() -> None:
    reset_scan_create_rate_limit_state()
    uid = uuid4()
    with patch("app.services.scan_create_rate_limit.settings") as s:
        s.scan_create_per_minute = 3
        check_scan_create_rate_limit(uid)
        check_scan_create_rate_limit(uid)
        check_scan_create_rate_limit(uid)


def test_rate_limit_blocks_excess() -> None:
    reset_scan_create_rate_limit_state()
    uid = uuid4()
    with patch("app.services.scan_create_rate_limit.settings") as s:
        s.scan_create_per_minute = 2
        check_scan_create_rate_limit(uid)
        check_scan_create_rate_limit(uid)
        with pytest.raises(HTTPException) as ei:
            check_scan_create_rate_limit(uid)
        assert ei.value.status_code == 429


def test_rate_limit_disabled_when_zero() -> None:
    reset_scan_create_rate_limit_state()
    uid = uuid4()
    with patch("app.services.scan_create_rate_limit.settings") as s:
        s.scan_create_per_minute = 0
        for _ in range(50):
            check_scan_create_rate_limit(uid)
