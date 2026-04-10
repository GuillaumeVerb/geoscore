"""
Lightweight HTTP fetch (docs/01-architecture/pipeline-analysis.md).
Playwright render is a deliberate placeholder — escalate later when bundled.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx

USER_AGENT = "GeoScore/0.1 (+https://github.com/GeoScore) analysis-fetch"


@dataclass
class FetchOutcome:
    ok: bool
    http_status: int | None
    final_url: str | None
    content_type: str | None
    html: str
    load_time_ms: int
    error_message: str | None = None
    is_blocked: bool = False
    has_auth_wall: bool = False


def http_fetch(url: str, timeout_sec: float = 18.0) -> FetchOutcome:
    start = time.perf_counter()
    try:
        with httpx.Client(
            timeout=timeout_sec,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"},
        ) as client:
            response = client.get(url)
    except httpx.RequestError as e:
        elapsed = int((time.perf_counter() - start) * 1000)
        return FetchOutcome(
            ok=False,
            http_status=None,
            final_url=None,
            content_type=None,
            html="",
            load_time_ms=elapsed,
            error_message=str(e)[:500],
        )

    elapsed = int((time.perf_counter() - start) * 1000)
    ct = response.headers.get("content-type", "").split(";")[0].strip() or None
    body = response.text if response.text else ""
    blocked = response.status_code in (401, 403, 429) or "captcha" in body.lower()[:2000]
    auth_wall = response.status_code in (401, 403)

    return FetchOutcome(
        ok=response.status_code < 400 and bool(body),
        http_status=response.status_code,
        final_url=str(response.url),
        content_type=ct,
        html=body,
        load_time_ms=elapsed,
        is_blocked=blocked,
        has_auth_wall=auth_wall,
    )


def fetch_diagnostics_dict(out: FetchOutcome) -> dict[str, Any]:
    return {
        "http_status": out.http_status,
        "final_url": out.final_url,
        "content_type": out.content_type,
        "html_length": len(out.html),
        "load_time_ms": out.load_time_ms,
        "error": out.error_message,
        "is_blocked": out.is_blocked,
        "has_auth_wall": out.has_auth_wall,
    }
