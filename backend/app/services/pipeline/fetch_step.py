"""
Lightweight HTTP fetch (docs/01-architecture/pipeline-analysis.md).
Browser-like headers improve HTML delivery from CDNs; Playwright covers JS shells.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx

# Chromium-style UA — many sites return minimal/shell HTML to non-browser or bot-looking agents.
BROWSER_LIKE_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 GeoScore/0.1"
)

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": BROWSER_LIKE_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


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


def _build_outcome_from_response(response: httpx.Response, elapsed_ms: int) -> FetchOutcome:
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
        load_time_ms=elapsed_ms,
        is_blocked=blocked,
        has_auth_wall=auth_wall,
    )


def _http_fetch_once(url: str, timeout_sec: float) -> FetchOutcome:
    start = time.perf_counter()
    try:
        with httpx.Client(
            timeout=timeout_sec,
            follow_redirects=True,
            headers=DEFAULT_REQUEST_HEADERS,
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
    return _build_outcome_from_response(response, elapsed)


def _should_retry_http(out: FetchOutcome) -> bool:
    """One follow-up attempt on transient network or origin overload."""
    if out.ok and (out.http_status is None or out.http_status < 400):
        return False
    if out.error_message:
        return True
    if out.http_status in (502, 503, 504):
        return True
    return False


def http_fetch(url: str, timeout_sec: float = 25.0, max_retries: int = 1) -> FetchOutcome:
    """
    GET the URL. Retries on connection errors and 502/502/504 (backoff 0.5s, 1s, …).
    `max_retries` is the number of *extra* attempts after the first.

    When the URL's host is listed in settings ``http_timeout_boost_hosts``,
    ``http_host_extra_timeout_sec`` is added to ``timeout_sec`` (slow CDNs / origins).
    """
    from app.core.config import settings
    from app.services.pipeline.host_config import url_host_in_csv

    effective_timeout = float(timeout_sec)
    if url_host_in_csv(url, settings.http_timeout_boost_hosts):
        effective_timeout += float(settings.http_host_extra_timeout_sec)

    attempts = 1 + max(0, max_retries)
    out: FetchOutcome | None = None
    for i in range(attempts):
        if i > 0:
            time.sleep(0.5 * i)
        out = _http_fetch_once(url, effective_timeout)
        if not _should_retry_http(out) or i == attempts - 1:
            return out
    return out  # type: ignore[unreachable]


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
