"""HTML selection after optional Playwright (no browser)."""

from __future__ import annotations

from app.services.pipeline.playwright_fetch import PlaywrightFetchResult, choose_html_after_playwright


def test_prefers_playwright_when_much_richer() -> None:
    http_html = "<html><body><p>short</p></body></html>"
    pw_html = "<html><body><h1>Hi</h1>" + ("<p>word</p>" * 50) + "</body></html>"
    pw = PlaywrightFetchResult(html=pw_html, final_url="https://example.com/x", load_time_ms=800, error=None)
    chosen, choice, diag = choose_html_after_playwright(http_html, pw)
    assert choice == "playwright"
    assert "Hi" in chosen
    assert diag.get("playwright_visible_words", 0) > diag.get("http_visible_words", 0)


def test_keeps_http_when_playwright_weak() -> None:
    http_html = "<html><body><h1>T</h1>" + ("<p>word</p>" * 40) + "</body></html>"
    pw_html = "<html><body><p>almost same</p></body></html>"
    pw = PlaywrightFetchResult(html=pw_html, final_url="https://example.com/", load_time_ms=100, error=None)
    chosen, choice, diag = choose_html_after_playwright(http_html, pw)
    assert choice == "http_kept_playwright_weak"
    assert diag.get("playwright_insufficient_gain") is True
    assert chosen == http_html


def test_import_error_skipped_uses_http() -> None:
    http_html = "<html><body>ok</body></html>"
    pw = PlaywrightFetchResult(
        html=None,
        final_url=None,
        load_time_ms=0,
        error=None,
        skipped_reason="playwright_package_not_installed",
    )
    chosen, choice, diag = choose_html_after_playwright(http_html, pw)
    assert choice == "http_only"
    assert chosen == http_html
    assert diag.get("playwright_skipped") == "playwright_package_not_installed"
