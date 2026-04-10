"""
Normalized extraction aligned with docs/02-scoring/extraction-schema-v1.md.
Deterministic DOM signals only (no Playwright). Scoring reads this payload, not raw HTML.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

from bs4 import BeautifulSoup, Tag

from app.services.pipeline.constants import EXTRACTION_VERSION

_NOISE_TAGS = frozenset({"script", "style", "noscript", "template", "svg"})
_CTA_RE = re.compile(
    r"\b(sign\s*up|get\s*started|try\s*(it|for)|book\s*a|request\s*a\s*demo|contact\s*(us)?|subscribe|buy\s*now|start\s*free)\b",
    re.I,
)
_OFFER_RE = re.compile(
    r"\b(pricing|plans?|per\s*month|/mo|free\s*trial|\$\d|€\d|£\d|upgrade|subscribe|license)\b",
    re.I,
)
_EXAMPLE_RE = re.compile(r"\b(example|e\.g\.|for\s+instance|such\s+as)\b", re.I)
_STEP_RE = re.compile(r"\b(step\s*\d|first,|second,|finally,)\b", re.I)
_FAQ_HEADING_RE = re.compile(
    r"\b(faq|frequently\s+asked|questions?\s*&?\s*answers?|common\s+questions)\b",
    re.I,
)


def build_extraction_payload(
    scan_id: UUID,
    normalized_url: str,
    fetch_info: dict[str, Any],
    render_info: dict[str, Any],
    html: str,
) -> dict[str, Any]:
    limitations: list[dict[str, str]] = []
    if not html or len(html) < 200:
        limitations.append(
            {
                "code": "THIN_CONTENT",
                "message": "Very little HTML received; extraction is shallow.",
                "severity": "warning",
            }
        )

    soup = BeautifulSoup(html or "", "html.parser")
    soup_for_structure = BeautifulSoup(html or "", "html.parser")
    _strip_noise(soup)

    main_text = soup.get_text(separator=" ", strip=True)
    word_count = len(main_text.split()) if main_text else 0
    char_count = len(main_text)

    meta = _extract_meta(soup_for_structure)
    headings = _extract_headings(soup_for_structure)
    links = _extract_links(soup_for_structure, normalized_url)
    media = _extract_media(soup_for_structure)
    page_features = _extract_page_features(soup_for_structure)
    structured_data = _extract_structured_data(soup_for_structure)
    trust_signals = _extract_trust_signals(soup_for_structure, links, structured_data)

    hero_text = _hero_visible_text(soup_for_structure)
    hero_words = len(hero_text.split()) if hero_text else 0
    faq_schema = bool(structured_data.get("has_faqpage_schema"))

    content = _build_content_block(
        soup_for_structure,
        main_text=main_text,
        word_count=word_count,
        char_count=char_count,
        hero_text=hero_text,
        hero_words=hero_words,
        headings=headings,
        faq_schema_present=faq_schema,
    )

    derived_metrics = _derive_metrics(
        word_count=word_count,
        headings=headings,
        content=content,
        links=links,
        media=media,
        structured_data=structured_data,
    )

    llm_payload_candidate = {
        "title": (meta.get("title") or "")[:200],
        "meta_description": (meta.get("meta_description") or "")[:300],
        "h1": (headings.get("h1") or [])[:3],
        "h2_sample": (headings.get("h2") or [])[:6],
        "hero_excerpt": hero_text[:500],
        "word_count": word_count,
        "has_faq_heuristic": bool(content.get("structural_features", {}).get("has_faq_section_heuristic")),
        "json_ld_types": structured_data.get("schema_types_found") or [],
    }

    return {
        "schema_version": EXTRACTION_VERSION,
        "scan_id": str(scan_id),
        "url_info": {"normalized_url": normalized_url},
        "fetch_info": fetch_info,
        "render_info": render_info,
        "page_detection": {},
        "meta": meta,
        "headings": headings,
        "content": content,
        "links": links,
        "media": media,
        "structured_data": structured_data,
        "trust_signals": trust_signals,
        "page_features": page_features,
        "derived_metrics": derived_metrics,
        "limitations": limitations,
        "llm_payload_candidate": llm_payload_candidate,
    }


def _strip_noise(soup: BeautifulSoup) -> None:
    for t in soup.find_all(list(_NOISE_TAGS)):
        t.decompose()


def _extract_meta(soup: BeautifulSoup) -> dict[str, Any]:
    title_tag = soup.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else ""
    meta_desc = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
    meta_desc_content = ""
    if meta_desc and meta_desc.get("content"):
        meta_desc_content = str(meta_desc.get("content", "")).strip()

    robots = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    robots_content = str(robots.get("content", "")).strip() if robots and robots.get("content") else None

    def _og(prop: str) -> str | None:
        m = soup.find("meta", attrs={"property": re.compile(rf"^{re.escape(prop)}$", re.I)})
        if m and m.get("content"):
            return str(m.get("content", "")).strip() or None
        return None

    tw_card = soup.find("meta", attrs={"name": re.compile(r"^twitter:card$", re.I)})
    tw_card_v = str(tw_card.get("content", "")).strip() if tw_card and tw_card.get("content") else None

    html_el = soup.find("html")
    lang = html_el.get("lang") if html_el else None
    if lang:
        lang = str(lang).strip() or None

    return {
        "title": title_text,
        "meta_description": meta_desc_content,
        "canonical": _first_link_rel(soup, "canonical"),
        "robots": robots_content,
        "og_title": _og("og:title"),
        "og_description": _og("og:description"),
        "og_type": _og("og:type"),
        "twitter_card": tw_card_v,
        "html_lang": lang,
    }


def _first_link_rel(soup: BeautifulSoup, rel: str) -> str | None:
    link = soup.find("link", attrs={"rel": re.compile(rel, re.I)})
    if link and link.get("href"):
        return str(link.get("href", "")).strip() or None
    return None


def _extract_headings(soup: BeautifulSoup) -> dict[str, Any]:
    h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2s = [h.get_text(strip=True) for h in soup.find_all("h2")][:30]
    h3s = [h.get_text(strip=True) for h in soup.find_all("h3")][:30]
    return {
        "h1": h1s,
        "h2": h2s,
        "h3": h3s,
        "h1_count": len(h1s),
        "h2_count": len(h2s),
        "h3_count": len(h3s),
    }


def _extract_links(soup: BeautifulSoup, normalized_url: str) -> dict[str, Any]:
    base_host = urlparse(normalized_url).netloc.lower()
    anchors = soup.find_all("a", href=True)
    internal = 0
    external = 0
    mailto = 0
    tel = 0
    sampled = 0
    descriptive_internals = 0

    for a in anchors[:800]:
        href = str(a.get("href", "")).strip()
        if not href or href.startswith(("#", "javascript:")):
            continue
        sampled += 1
        ht = href.lower()
        if ht.startswith("mailto:"):
            mailto += 1
            continue
        if ht.startswith("tel:"):
            tel += 1
            continue
        text = a.get_text(strip=True)
        text_len = len(text.split())
        if href.startswith("http") and base_host and base_host not in ht:
            external += 1
        else:
            internal += 1
            if text_len >= 3:
                descriptive_internals += 1

    return {
        "internal_count": internal,
        "external_count": external,
        "mailto_count": mailto,
        "tel_count": tel,
        "total_sampled": sampled,
        "internal_with_descriptive_anchor_3plus_words": descriptive_internals,
    }


def _extract_media(soup: BeautifulSoup) -> dict[str, Any]:
    imgs = soup.find_all("img")
    with_alt = 0
    without_alt = 0
    for im in imgs:
        alt = im.get("alt")
        if alt is not None and str(alt).strip():
            with_alt += 1
        else:
            without_alt += 1
    n = len(imgs)
    return {
        "image_count": n,
        "images_with_alt": with_alt,
        "images_without_alt": without_alt,
        "images_alt_ratio": round(with_alt / n, 3) if n else 0.0,
        "video_tag_count": len(soup.find_all("video")),
    }


def _extract_structured_data(soup: BeautifulSoup) -> dict[str, Any]:
    scripts = soup.find_all("script", type=re.compile(r"application/ld\+json", re.I))
    types_found: list[str] = []
    faq_schema = False
    for sc in scripts[:20]:
        raw = sc.string or sc.get_text() or ""
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for t in _walk_schema_types(data):
            types_found.append(t)
            if t.upper() == "FAQPAGE":
                faq_schema = True

    # de-dupe preserving order
    seen: set[str] = set()
    unique_types: list[str] = []
    for t in types_found:
        tl = t.strip()
        if tl and tl not in seen:
            seen.add(tl)
            unique_types.append(tl)

    return {
        "json_ld_scripts": len(scripts),
        "schema_types_found": unique_types[:25],
        "has_faqpage_schema": faq_schema,
    }


def _walk_schema_types(node: Any) -> list[str]:
    out: list[str] = []
    if isinstance(node, dict):
        t = node.get("@type")
        if isinstance(t, str):
            out.append(t)
        elif isinstance(t, list):
            for x in t:
                if isinstance(x, str):
                    out.append(x)
        for v in node.values():
            out.extend(_walk_schema_types(v))
    elif isinstance(node, list):
        for item in node:
            out.extend(_walk_schema_types(item))
    return out


def _extract_page_features(soup: BeautifulSoup) -> dict[str, Any]:
    return {
        "has_viewport": bool(soup.find("meta", attrs={"name": re.compile(r"viewport", re.I)})),
        "has_open_graph": bool(soup.find("meta", attrs={"property": re.compile(r"^og:", re.I)})),
        "has_twitter_card": bool(soup.find("meta", attrs={"name": re.compile(r"^twitter:", re.I)})),
        "has_theme_color": bool(soup.find("meta", attrs={"name": re.compile(r"theme-color", re.I)})),
    }


def _extract_trust_signals(
    soup: BeautifulSoup,
    links: dict[str, Any],
    structured_data: dict[str, Any],
) -> dict[str, Any]:
    types = [t.lower() for t in (structured_data.get("schema_types_found") or [])]
    org_hit = any("organization" in t or "corporation" in t or "localbusiness" in t for t in types)
    product_hit = any("product" in t for t in types)
    website_hit = any("website" in t or "webpage" in t for t in types)

    blob = soup.get_text("\n", strip=True).lower()
    privacy = "privacy policy" in blob or bool(soup.find("a", href=re.compile(r"privacy", re.I)))

    return {
        "contact_mailto_count": int(links.get("mailto_count") or 0),
        "contact_tel_count": int(links.get("tel_count") or 0),
        "has_organization_like_schema": org_hit,
        "has_product_schema": product_hit,
        "has_website_or_webpage_schema": website_hit,
        "privacy_policy_signal": privacy,
        "schema_type_count": len(structured_data.get("schema_types_found") or []),
    }


def _hero_visible_text(soup: BeautifulSoup) -> str:
    for sel in ("main", "article", '[role="main"]'):
        el = soup.select_one(sel)
        if isinstance(el, Tag):
            t = el.get_text(separator=" ", strip=True)
            if len(t.split()) >= 8:
                return t[:2000]
    body = soup.body
    if isinstance(body, Tag):
        return body.get_text(separator=" ", strip=True)[:2000]
    return ""


def _build_content_block(
    soup: BeautifulSoup,
    *,
    main_text: str,
    word_count: int,
    char_count: int,
    hero_text: str,
    hero_words: int,
    headings: dict[str, Any],
    faq_schema_present: bool,
) -> dict[str, Any]:
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    p_count = len(paragraphs)
    sentence_appr = max(1, main_text.count(".") + main_text.count("!") + main_text.count("?"))
    avg_wp = round(word_count / p_count, 1) if p_count else 0.0

    list_items = 0
    for lst in soup.find_all(["ul", "ol"]):
        list_items += len(lst.find_all("li", recursive=False))
    table_count = len(soup.find_all("table"))

    h2_texts = headings.get("h2") or []
    h3_texts = headings.get("h3") or []
    faq_heading_hits = sum(1 for h in (h2_texts + h3_texts) if isinstance(h, str) and _FAQ_HEADING_RE.search(h))
    has_faq_section = faq_heading_hits > 0 or bool(soup.find(id=re.compile(r"faq", re.I)))

    numbered = bool(soup.find(attrs={"class": re.compile(r"step|numbered|timeline", re.I)})) or bool(
        _STEP_RE.search(main_text[:3000])
    )
    bullets = list_items > 0

    body_wo_hero_words = max(0, word_count - min(hero_words, word_count))

    how_what_why = sum(
        1
        for h in (h2_texts + h3_texts)
        if isinstance(h, str) and re.match(r"^\s*(how|what|why|when|where|who)\b", h, re.I)
    )

    question_marks = main_text.count("?")

    numeric_hits = len(re.findall(r"\b\d{1,3}(?:[.,]\d{3})+\b|\b\d+\b", main_text[:8000]))
    currency_hits = len(re.findall(r"[$€£]\s*\d|\d+\s*(?:€|usd|eur|gbp|/mo|per\s+month)\b", main_text, re.I))
    year_hits = len(re.findall(r"\b(19|20)\d{2}\b", main_text))
    example_hits = len(_EXAMPLE_RE.findall(main_text))
    step_hits = len(_STEP_RE.findall(main_text[:6000]))

    numeric_density = round(min(100.0, (numeric_hits / max(1, word_count)) * 120.0), 1)

    first_h = None
    for tag in ("h1", "h2"):
        el = soup.find(tag)
        if el:
            first_h = el.get_text(strip=True)[:200]
            break

    return {
        "word_count": word_count,
        "char_count": char_count,
        "raw_metrics": {
            "paragraph_count": p_count,
            "sentence_count_approx": sentence_appr,
            "avg_words_per_paragraph": avg_wp,
            "list_item_count": list_items,
            "blockquote_count": len(soup.find_all("blockquote")),
        },
        "hero": {
            "approx_word_count": hero_words,
            "first_heading_text": first_h,
            "has_cta_language": bool(_CTA_RE.search(hero_text)),
            "snippet": hero_text[:280],
            "offer_language_hits": len(_OFFER_RE.findall(hero_text)),
        },
        "main_body": {
            "word_count_ex_hero_estimate": body_wo_hero_words,
            "paragraph_count_body_estimate": max(0, p_count - 1),
        },
        "structural_features": {
            "has_faq_section_heuristic": has_faq_section,
            "faq_like_heading_count": faq_heading_hits,
            "has_numbered_steps_heuristic": numbered,
            "has_bullet_or_list_content": bullets,
            "table_count": table_count,
            "h2_count": int(headings.get("h2_count") or 0),
            "h3_count": int(headings.get("h3_count") or 0),
        },
        "precision_features": {
            "currency_or_price_mentions": currency_hits,
            "year_mentions": year_hits,
            "numeric_token_density_index": numeric_density,
            "example_phrase_hits": example_hits,
            "step_language_hits": step_hits,
        },
        "answerability_features": {
            "question_marks_in_body": question_marks,
            "faq_schema_present": faq_schema_present,
            "how_what_why_heading_count": how_what_why,
        },
    }


def _derive_metrics(
    *,
    word_count: int,
    headings: dict[str, Any],
    content: dict[str, Any],
    links: dict[str, Any],
    media: dict[str, Any],
    structured_data: dict[str, Any],
) -> dict[str, Any]:
    struct = content.get("structural_features") or {}
    prec = content.get("precision_features") or {}
    answ = content.get("answerability_features") or {}
    raw_m = content.get("raw_metrics") or {}
    h1c = int(headings.get("h1_count") or 0)
    h2c = int(struct.get("h2_count") or 0)

    heading_depth_ratio = round((h1c + h2c) / max(1, word_count / 200.0), 3)
    list_item_count = int(raw_m.get("list_item_count") or 0)
    list_density = round(list_item_count / max(1, word_count / 50.0), 3)

    citation_readiness_index = round(
        min(
            100.0,
            (prec.get("example_phrase_hits", 0) + prec.get("step_language_hits", 0)) * 8.0
            + float(prec.get("numeric_token_density_index", 0) or 0) * 0.35
            + (10.0 if structured_data.get("json_ld_scripts") else 0.0),
        ),
        1,
    )

    extractability_index = round(
        min(
            100.0,
            list_item_count * 2.5
            + (answ.get("how_what_why_heading_count", 0) or 0) * 12.0
            + (20.0 if struct.get("has_faq_section_heuristic") else 0.0)
            + (15.0 if answ.get("faq_schema_present") else 0.0)
            + min(30.0, (answ.get("question_marks_in_body", 0) or 0) * 2.0),
        ),
        1,
    )

    return {
        "words_per_heading_tier": heading_depth_ratio,
        "list_density_index": list_density,
        "citation_readiness_index": citation_readiness_index,
        "extractability_index": extractability_index,
        "internal_link_ratio_sampled": round(
            (links.get("internal_count") or 0) / max(1, (links.get("total_sampled") or 1)), 3
        ),
        "media_alt_health": round(float(media.get("images_alt_ratio") or 0.0) * 100.0, 1),
    }
