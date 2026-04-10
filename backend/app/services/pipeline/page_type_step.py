"""Heuristic page type (pipeline-analysis.md §5). PLACEHOLDER: richer NLP / structure signals later."""

from __future__ import annotations

import re


def detect_page_type(path: str, title: str, h1_texts: list[str]) -> tuple[str, float]:
    p = path.lower() or "/"
    blob = f"{title} {' '.join(h1_texts)}".lower()

    if p.rstrip("/") == "" or p == "/":
        return "homepage", 0.75
    if re.search(r"/(pricing|plans?)(/|$)", p):
        return "pricing_page", 0.7
    if re.search(r"/(product|shop|store|p/)(/|$)", p):
        return "product_page", 0.55
    if re.search(r"/(blog|article|news|posts?)(/|$)", p) or "blog" in blob[:80]:
        return "article", 0.55
    if re.search(r"/(about|team|company)(/|$)", p):
        return "about_page", 0.65
    if re.search(r"/(app|download|ios|android)(/|$)", p):
        return "app_page", 0.5
    if re.search(r"/(lp|landing)(/|$)", p) or "landing" in blob[:60]:
        return "landing_page", 0.45
    return "other", 0.35
