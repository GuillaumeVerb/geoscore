"""Structured one-line logging for scan pipeline outcomes (ops / observability)."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

logger = logging.getLogger(__name__)


def _host_from_url(url: str) -> str:
    try:
        h = urlparse(url).hostname or ""
        return h[:200] if h else ""
    except (ValueError, TypeError, AttributeError):
        return ""


def log_scan_pipeline_outcome(
    scan_id: UUID,
    normalized_url: str,
    *,
    final_status: str,
    error_code: str | None = None,
    partial: bool | None = None,
    fetch_method: str | None = None,
    load_time_ms: int | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """
    One line per terminal pipeline state — easy to grep and ship to log aggregation.
    """
    parts = [
        f"scan_pipeline_outcome scan_id={scan_id}",
        f"host={_host_from_url(normalized_url) or '—'}",
        f"final_status={final_status}",
    ]
    if error_code:
        parts.append(f"error_code={error_code}")
    if partial is not None:
        parts.append(f"partial={partial}")
    if fetch_method:
        parts.append(f"fetch_method={fetch_method}")
    if load_time_ms is not None:
        parts.append(f"load_time_ms={load_time_ms}")
    if extra:
        for k, v in extra.items():
            if v is not None:
                parts.append(f"{k}={v}")
    logger.info(" ".join(parts))
