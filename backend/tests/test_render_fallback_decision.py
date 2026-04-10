"""Decision logic for optional Playwright fallback (no browser)."""

from __future__ import annotations

from app.services.pipeline.fetch_step import FetchOutcome
from app.services.pipeline.render_fallback_decision import (
    analyze_http_html_signals,
    count_spa_signals,
    should_trigger_playwright_fallback,
    visible_text_metrics,
)


def _ok_out() -> FetchOutcome:
    return FetchOutcome(
        ok=True,
        http_status=200,
        final_url="https://example.com/pricing",
        content_type="text/html",
        html="",
        load_time_ms=10,
    )


def test_visible_text_strips_scripts() -> None:
    html = "<html><script>x</script><body><p>hello world</p></body></html>"
    w, char_len = visible_text_metrics(html)
    assert w == 2
    assert char_len >= len("hello world")


def test_shell_html_triggers_fallback() -> None:
    # Large HTML, almost no visible text (simulates CSR shell)
    filler = "<div></div>" * 400
    html = f"<html><head><title>Amazing Product Pricing</title></head><body>{filler}</body></html>"
    out = _ok_out()
    out.html = html
    trigger, sig = should_trigger_playwright_fallback(html, "/pricing", out)
    assert trigger is True
    assert "large_html_few_visible_words" in sig.reasons_would_fallback or "thin_visible_on_heavy_document" in (
        sig.reasons_would_fallback
    )


def test_spa_signals_with_low_text() -> None:
    html = """
    <html><head><title>App</title><script>window.__NEXT_DATA__={}</script></head>
    <body><div id="root"></div></body></html>
    """
    n, hits = count_spa_signals(html)
    assert n >= 2
    out = _ok_out()
    out.html = html
    trigger, _ = should_trigger_playwright_fallback(html, "/", out)
    assert trigger is True


def test_substantial_page_no_fallback() -> None:
    body = "<h1>Topic</h1>" + "<p>word </p>" * 80
    html = f"<html><head><title>Nice title here</title></head><body>{body}</body></html>"
    out = _ok_out()
    out.html = html
    trigger, sig = should_trigger_playwright_fallback(html, "/blog/post", out)
    assert trigger is False
    assert sig.visible_word_count > 50


def test_marketing_path_no_headings() -> None:
    filler = "x" * 8000
    html = f"<html><head><title>Product suite for teams</title></head><body><div>{filler}</div></body></html>"
    out = _ok_out()
    out.html = html
    trigger, sig = should_trigger_playwright_fallback(html, "/product/overview", out)
    assert trigger is True
    assert "marketing_path_no_headings_heavy_html" in sig.reasons_would_fallback


def test_http_error_does_not_trigger_playwright_flag() -> None:
    html = "<html>bad</html>"
    out = FetchOutcome(
        ok=False,
        http_status=500,
        final_url="https://example.com",
        content_type="text/html",
        html=html,
        load_time_ms=5,
    )
    trigger, _ = should_trigger_playwright_fallback(html, "/", out)
    assert trigger is False


def test_analyze_signals_includes_title() -> None:
    html = "<html><head><title>Hello world title</title></head><body><p>a</p></body></html>"
    sig = analyze_http_html_signals(html, "/")
    assert "Hello" in sig.title_text
