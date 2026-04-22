"""
In-process rate limit for new scans and rescans (per user id).
Used by POST /api/scans and POST /api/scans/{id}/rescan — same rolling window and quota.

Sufficient for a single API instance; for horizontal scale, use Redis + a shared limiter.
"""

from __future__ import annotations

import time
from threading import Lock
from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import settings

# user_id str -> list of request timestamps (last 60s)
_bucket: dict[str, list[float]] = {}
_lock = Lock()


def reset_scan_create_rate_limit_state() -> None:
    """Test helper: clear rolling windows (e.g. between unit tests)."""
    with _lock:
        _bucket.clear()


def check_scan_create_rate_limit(user_id: UUID) -> None:
    """Raises 429 if the user exceeded allowed new-scan + rescan operations in the rolling window."""
    limit = int(settings.scan_create_per_minute)
    if limit <= 0:
        return
    key = str(user_id)
    now = time.time()
    window = 60.0
    with _lock:
        cut = now - window
        times = [t for t in _bucket.get(key, []) if t > cut]
        if len(times) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many scan requests. Please wait a minute and try again.",
            )
        times.append(now)
        _bucket[key] = times
