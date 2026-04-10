"""
Optional headless Chromium render (Playwright). Used only as fallback after HTTP fetch.
Install: pip install playwright && playwright install chromium
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PlaywrightFetchResult:
    html: str | None
    final_url: str | None
    load_time_ms: int
    error: str | None = None
    skipped_reason: str | None = None  # disabled, import_error, exception


def playwright_fetch_html(url: str, *, timeout_ms: int, settle_ms: int = 1_200) -> PlaywrightFetchResult:
    """
    Load URL in headless Chromium; return serialized DOM.

    wait_until=domcontentloaded avoids hanging on long-polling SPAs; short settle allows hydration.
    """
    start = time.perf_counter()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return PlaywrightFetchResult(
            None,
            None,
            0,
            error=None,
            skipped_reason="playwright_package_not_installed",
        )

    browser = None
    playwright = None
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        if settle_ms > 0:
            page.wait_for_timeout(settle_ms)
        html = page.content()
        final = page.url
        elapsed = int((time.perf_counter() - start) * 1000)
        return PlaywrightFetchResult(html=html, final_url=final, load_time_ms=elapsed, error=None)
    except Exception as e:
        elapsed = int((time.perf_counter() - start) * 1000)
        msg = str(e)[:500]
        logger.warning("playwright fetch failed url=%s err=%s", url, msg)
        return PlaywrightFetchResult(
            html=None,
            final_url=None,
            load_time_ms=elapsed,
            error=msg,
            skipped_reason="exception",
        )
    finally:
        try:
            if browser:
                browser.close()
        except Exception:
            logger.exception("playwright browser.close failed")
        try:
            if playwright:
                playwright.stop()
        except Exception:
            logger.exception("playwright.stop failed")


def choose_html_after_playwright(
    http_html: str,
    pw: PlaywrightFetchResult | None,
) -> tuple[str, str, dict[str, Any]]:
    """
    Pick HTML for extraction. Returns (html, choice, diagnostics).

    choice: http_only | playwright | http_kept_playwright_weak
    """
    from app.services.pipeline.render_fallback_decision import visible_text_metrics

    w_http, _ = visible_text_metrics(http_html)
    diag: dict[str, Any] = {
        "playwright_attempted": False,
        "http_visible_words": w_http,
    }
    if pw is None:
        return http_html, "http_only", diag

    diag["playwright_attempted"] = True
    if pw.skipped_reason and not pw.html:
        diag["playwright_skipped"] = pw.skipped_reason
        if pw.error:
            diag["playwright_error"] = pw.error
        return http_html, "http_only", diag

    diag["playwright_load_time_ms"] = pw.load_time_ms
    if pw.error and not pw.html:
        diag["playwright_error"] = pw.error
        return http_html, "http_only", diag

    if not pw.html:
        diag["playwright_error"] = "empty_html"
        return http_html, "http_only", diag

    w_pw, _ = visible_text_metrics(pw.html)
    diag["playwright_visible_words"] = w_pw
    diag["playwright_final_url"] = pw.final_url

    # Prefer Playwright when it clearly adds rendered content
    if w_pw >= w_http + 25:
        return pw.html, "playwright", diag
    if w_pw > max(90, int(w_http * 1.25)):
        return pw.html, "playwright", diag

    diag["playwright_insufficient_gain"] = True
    return http_html, "http_kept_playwright_weak", diag
