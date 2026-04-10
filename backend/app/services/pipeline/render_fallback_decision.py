"""
Explicit criteria for optional Playwright fallback after HTTP fetch (pipeline-analysis.md).
Pure functions — no I/O; covered by unit tests.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from bs4 import BeautifulSoup

from app.services.pipeline.fetch_step import FetchOutcome

# --- Tunable thresholds (MVP) ---
SHELL_HTML_MIN_BYTES = 3_500
LARGE_HTML_MIN_BYTES = 7_000
# Very little usable text vs HTML weight → likely client-rendered shell
VISIBLE_WORDS_VS_SHELL = 70
# SPA / JS-heavy hints + low text
SPA_LOW_WORDS_MAX = 120
# Marketing-like paths with no headings but big HTML
MARKETING_PATH_MAX_HEADINGS_TOTAL = 0
MARKETING_PATH_MAX_VISIBLE_WORDS = 150
# Title present but almost no body (SSR title only)
TITLE_BODY_MISMATCH_TITLE_MIN = 12
TITLE_BODY_MISMATCH_MAX_WORDS = 35
# Generic thin content on heavy document
THIN_ON_HEAVY_MAX_WORDS = 45
THIN_ON_HEAVY_MIN_BYTES = 5_000

_MARKETING_PATH_RE = re.compile(
    r"/(pricing|price|plans?|product|features|solutions|platform|demo|trial|signup|sign-up|landing|lp)(/|$)",
    re.I,
)


@dataclass
class HttpHtmlSignals:
    """Lightweight parse of HTTP HTML for fallback decision only."""

    html_byte_len: int
    visible_word_count: int
    visible_char_count: int
    h1_count: int
    h2_count: int
    title_text: str
    spa_signal_score: int
    spa_signals_hit: list[str] = field(default_factory=list)
    reasons_would_fallback: list[str] = field(default_factory=list)


def _strip_for_visible_text(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html or "", "html.parser")
    for t in soup(["script", "style", "noscript", "template"]):
        t.decompose()
    return soup


def visible_text_metrics(html: str) -> tuple[int, int]:
    """Return (word_count, char_count) of visible text after removing script/style."""
    soup = _strip_for_visible_text(html)
    text = soup.get_text(separator=" ", strip=True)
    words = text.split()
    return len(words), len(text)


def quick_heading_title_metrics(html: str) -> tuple[int, int, str]:
    soup = BeautifulSoup(html or "", "html.parser")
    h1 = len(soup.find_all("h1"))
    h2 = len(soup.find_all("h2"))
    tt = soup.find("title")
    title = tt.get_text(strip=True) if tt else ""
    return h1, h2, title


def count_spa_signals(raw_html: str) -> tuple[int, list[str]]:
    """Heuristic JS/SPA markers in raw HTML (not visible text)."""
    h = raw_html or ""
    hits: list[str] = []
    if "__NEXT_DATA__" in h:
        hits.append("next_data")
    if re.search(r'id=["\']__next["\']', h) or re.search(r'id=["\']root["\']', h):
        hits.append("common_root_id")
    if "data-reactroot" in h or "data-react-root" in h:
        hits.append("react_root_attr")
    if re.search(r'<div[^>]+id=["\']app["\']', h, re.I):
        hits.append("div_id_app")
    if re.search(r"webpackJsonp|chunk\.js|static/chunks/", h):
        hits.append("webpack_chunks")
    if h.count("<script") >= 8 and len(h) > 10_000:
        hits.append("many_script_tags")
    return len(hits), hits


def analyze_http_html_signals(html: str, url_path: str) -> HttpHtmlSignals:
    path = url_path or "/"
    vw, vc = visible_text_metrics(html)
    h1, h2, title = quick_heading_title_metrics(html)
    spa_n, spa_hits = count_spa_signals(html)
    blen = len(html or "")

    reasons: list[str] = []

    if blen >= SHELL_HTML_MIN_BYTES and vw < VISIBLE_WORDS_VS_SHELL:
        reasons.append("large_html_few_visible_words")
    if spa_n >= 2 and vw < SPA_LOW_WORDS_MAX:
        reasons.append("spa_signals_with_low_text")
    if _MARKETING_PATH_RE.search(path) and (h1 + h2) <= MARKETING_PATH_MAX_HEADINGS_TOTAL:
        if blen >= LARGE_HTML_MIN_BYTES and vw < MARKETING_PATH_MAX_VISIBLE_WORDS:
            reasons.append("marketing_path_no_headings_heavy_html")
    if len(title.strip()) >= TITLE_BODY_MISMATCH_TITLE_MIN and vw < TITLE_BODY_MISMATCH_MAX_WORDS:
        reasons.append("title_substantial_but_body_tiny")
    if blen >= THIN_ON_HEAVY_MIN_BYTES and vw < THIN_ON_HEAVY_MAX_WORDS:
        reasons.append("thin_visible_on_heavy_document")

    return HttpHtmlSignals(
        html_byte_len=blen,
        visible_word_count=vw,
        visible_char_count=vc,
        h1_count=h1,
        h2_count=h2,
        title_text=title.strip(),
        spa_signal_score=spa_n,
        spa_signals_hit=spa_hits,
        reasons_would_fallback=reasons,
    )


def should_trigger_playwright_fallback(
    html: str,
    url_path: str,
    http_out: FetchOutcome,
) -> tuple[bool, HttpHtmlSignals]:
    """
    Return (trigger, signals).

    Never trigger when HTTP response is unusable (caller should handle 4xx / empty separately).
    """
    if not http_out.ok or (http_out.http_status is not None and http_out.http_status >= 400):
        return False, analyze_http_html_signals(html, url_path)
    if not (html or "").strip():
        return False, analyze_http_html_signals(html, url_path)

    sig = analyze_http_html_signals(html, url_path)
    trigger = bool(sig.reasons_would_fallback)
    return trigger, sig


def is_probably_spa(signals: HttpHtmlSignals) -> bool:
    return signals.spa_signal_score >= 2 or bool(signals.reasons_would_fallback)
