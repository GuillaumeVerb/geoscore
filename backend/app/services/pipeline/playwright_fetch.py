"""
Optional headless Chromium render (Playwright). Used only as fallback after HTTP fetch.
Install: pip install playwright && playwright install chromium
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from app.services.pipeline.fetch_step import BROWSER_LIKE_USER_AGENT

logger = logging.getLogger(__name__)


@dataclass
class PlaywrightFetchResult:
    html: str | None
    final_url: str | None
    load_time_ms: int
    error: str | None = None
    skipped_reason: str | None = None  # disabled, import_error, exception
    attempt: int = 1


def _install_heavy_resource_block(page: Any) -> None:
    """Skip images, fonts, media — faster loads and fewer hangs; text extraction does not need them."""

    def handle(route: Any) -> None:
        try:
            if route.request.resource_type in ("image", "media", "font"):
                route.abort()
            else:
                route.continue_()
        except Exception:
            try:
                route.continue_()
            except Exception:
                pass

    page.route("**/*", handle)


def _run_playwright_once(
    url: str,
    *,
    timeout_ms: int,
    settle_ms: int,
    wait_for_load_state: bool,
    load_state_timeout_ms: int,
    block_heavy_resources: bool,
) -> PlaywrightFetchResult:
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

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    user_agent=BROWSER_LIKE_USER_AGENT,
                    locale="en-US",
                    viewport={"width": 1280, "height": 720},
                )
                page = context.new_page()
                if block_heavy_resources:
                    _install_heavy_resource_block(page)

                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                if wait_for_load_state:
                    try:
                        page.wait_for_load_state("load", timeout=load_state_timeout_ms)
                    except Exception as e:
                        logger.debug("playwright load state wait skipped or timed out url=%s err=%s", url, e)
                if settle_ms > 0:
                    page.wait_for_timeout(settle_ms)
                html = page.content()
                final = page.url
                elapsed = int((time.perf_counter() - start) * 1000)
                try:
                    context.close()
                except Exception:
                    pass
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
                    browser.close()
                except Exception:
                    logger.exception("playwright browser.close failed")
    except Exception as e:
        elapsed = int((time.perf_counter() - start) * 1000)
        msg = str(e)[:500]
        logger.warning("playwright fetch failed (outer) url=%s err=%s", url, msg)
        return PlaywrightFetchResult(
            html=None,
            final_url=None,
            load_time_ms=elapsed,
            error=msg,
            skipped_reason="exception",
        )


def playwright_fetch_html(
    url: str,
    *,
    timeout_ms: int,
    settle_ms: int = 1_200,
    wait_for_load_state: bool = True,
    load_state_timeout_ms: int = 8_000,
    block_heavy_resources: bool = True,
    retry: bool = True,
) -> PlaywrightFetchResult:
    """
    Load URL in headless Chromium; return serialized DOM.

    - domcontentloaded + optional `load` + settle gives SPAs time to hydrate.
    - Heavy resources can be blocked to stay within budget and avoid hanging on large assets.
    - Optional second attempt on empty HTML or error (same parameters).
    - Per-host overrides: ``playwright_resource_block_exempt_hosts``, ``playwright_timeout_boost_hosts`` (see Settings).
    """
    from app.core.config import settings
    from app.services.pipeline.host_config import url_host_in_csv

    eff_timeout = int(timeout_ms)
    eff_load = int(load_state_timeout_ms)
    if url_host_in_csv(url, settings.playwright_timeout_boost_hosts):
        b = int(settings.playwright_host_timeout_boost_ms)
        eff_timeout += b
        eff_load += min(20_000, b)

    eff_block = bool(block_heavy_resources)
    if eff_block and url_host_in_csv(url, settings.playwright_resource_block_exempt_hosts):
        eff_block = False

    first = _run_playwright_once(
        url,
        timeout_ms=eff_timeout,
        settle_ms=settle_ms,
        wait_for_load_state=wait_for_load_state,
        load_state_timeout_ms=eff_load,
        block_heavy_resources=eff_block,
    )
    if not retry:
        return first
    if first.skipped_reason == "playwright_package_not_installed":
        return first
    if first.html and first.html.strip():
        return first
    second = _run_playwright_once(
        url,
        timeout_ms=eff_timeout,
        settle_ms=min(2_200, int(settle_ms * 1.3) or 1_500),
        wait_for_load_state=wait_for_load_state,
        load_state_timeout_ms=min(12_000, int(eff_load * 1.25)),
        block_heavy_resources=eff_block,
    )
    second.attempt = 2
    if not second.html and first.html:
        return first
    if first.html and second.html and len((second.html or "").strip()) < len((first.html or "").strip()) * 0.8:
        return first
    return second


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
    if pw.attempt > 1:
        diag["playwright_attempts"] = pw.attempt
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
