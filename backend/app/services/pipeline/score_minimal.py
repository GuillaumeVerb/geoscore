"""
Deterministic V1 scoring: SEO + GEO pillars, catalog-oriented rule codes (rules-catalog-v1.md).
Weighted subscores; issues map to stable recommendation keys (recommendations-mapping.md).
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from app.domain.enums import AnalysisConfidence
from app.schemas.issue import Issue
from app.schemas.limitation import Limitation
from app.schemas.recommendation import Recommendation

from app.services.pipeline.constants import (
    FETCH_METHOD_HTTP_PLAYWRIGHT_ATTEMPTED,
    RULESET_VERSION,
    SCORING_VERSION,
)


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def _dedupe_recommendations(recs: list[Recommendation]) -> list[Recommendation]:
    by_key: dict[str, Recommendation] = {}
    for r in recs:
        k = (r.key or r.title).strip()
        if not k:
            continue
        if k not in by_key or (r.priority or 99) < (by_key[k].priority or 99):
            by_key[k] = r
    return sorted(by_key.values(), key=lambda x: (x.priority or 99, x.title))


def _merge_hero_offer_recommendations(recs: list[Recommendation]) -> list[Recommendation]:
    """Single product-facing reco when both hero and offer nags fire (cal-02)."""
    keys = {r.key for r in recs if r.key}
    if "REWRITE_HERO" not in keys or "CLARIFY_OFFER_POSITIONING" not in keys:
        return recs
    pr = min(
        (r.priority or 99) for r in recs if r.key in ("REWRITE_HERO", "CLARIFY_OFFER_POSITIONING")
    )
    filtered = [r for r in recs if r.key not in ("REWRITE_HERO", "CLARIFY_OFFER_POSITIONING")]
    filtered.append(
        Recommendation(
            key="ABOVE_FOLD_CLARITY",
            title="Clarify the hero message and what you offer",
            explanation=(
                "State the value proposition, audience, and primary action above the fold; "
                "make the offer or entry point obvious for humans and parsers."
            ),
            impact_scope="geo",
            priority=pr,
            effort="medium",
            expected_gain="Clearer commercial intent and extractability",
        )
    )
    return filtered


def _cap_recommendation_list(recs: list[Recommendation], limit: int = 6) -> list[Recommendation]:
    return sorted(recs, key=lambda r: (r.priority or 99, r.title or ""))[:limit]


_HEADING_RECO_TITLE = "Improve heading structure"
_HEADING_RECO_EXPL_H1 = "Use one clear H1 for the main topic; add H2s for major sections."
_HEADING_RECO_EXPL_MULTI = "Use a single H1 and demote extra headings to H2/H3 where appropriate."
_HEADING_RECO_EXPL_H2 = "Add H2 section labels so long content is easier to scan and parse."


def _page_type_weights(page_type: str) -> tuple[dict[str, float], dict[str, float]]:
    seo = {k: 1.0 for k in ("title_meta", "heading_structure", "content_depth", "internal_links")}
    geo = {k: 1.0 for k in ("hero_clarity", "offer_clarity", "extractability", "citation_readiness", "trust_entity")}
    if page_type == "landing_page":
        geo["hero_clarity"] *= 1.18
        geo["offer_clarity"] *= 1.12
    elif page_type == "homepage":
        geo["hero_clarity"] *= 1.12
        geo["offer_clarity"] *= 1.08
    elif page_type == "product_page":
        geo["offer_clarity"] *= 1.15
        geo["citation_readiness"] *= 1.08
    elif page_type == "pricing_page":
        geo["offer_clarity"] *= 1.22
    elif page_type == "article":
        seo["content_depth"] *= 1.14
        geo["citation_readiness"] *= 1.12
        geo["hero_clarity"] *= 0.92
    return seo, geo


def _weighted_avg(scores: dict[str, float], weights: dict[str, float]) -> float:
    num = sum(scores[k] * weights.get(k, 1.0) for k in scores)
    den = sum(weights.get(k, 1.0) for k in scores)
    return _clamp(num / den) if den else 0.0


# cal-03: URL/path hints that this is documentation or editorial, not a commercial surface.
_DOC_PATH_PREFIXES = (
    "/docs",
    "/documentation",
    "/doc/",
    "/guide/",
    "/guides/",
    "/reference",
    "/api/",
    "/learn",
    "/tutorial",
)
_DOC_HOSTS_ROOT = frozenset({"react.dev", "www.react.dev"})


def _is_docs_editorial_like(
    extraction: dict[str, Any],
    page_type: str,
    *,
    word_count: int,
    h2_count: int,
    internal_links_count: int,
) -> bool:
    """
    Light heuristic only — does not replace page_type. When true, skip commercial hero/offer nags.
    """
    ui = extraction.get("url_info") or {}
    norm = (ui.get("normalized_url") or "").strip()
    if not norm:
        return False
    try:
        parsed = urlparse(norm)
    except Exception:
        return False
    host = (parsed.netloc or "").lower()
    if "@" in host:
        host = host.split("@")[-1]
    host_cmp = host[4:] if host.startswith("www.") else host
    path = (parsed.path or "/").lower()
    if not path.startswith("/"):
        path = "/" + path

    for pref in _DOC_PATH_PREFIXES:
        if path == pref.rstrip("/") or path.startswith(pref):
            return True
    if path == "/blog" or path.startswith("/blog/"):
        return True

    if host_cmp in _DOC_HOSTS_ROOT:
        return True
    if "nextjs.org" in host_cmp and (path == "/" or path.startswith("/docs") or path.startswith("/learn")):
        return True

    # Long structured technical pages mis-tagged as non-article (provisional; cal-03)
    if page_type in ("article", "about_page", "other"):
        if word_count >= 400 and h2_count >= 4 and internal_links_count >= 12:
            return True

    return False


def run_deterministic_score(
    extraction: dict[str, Any],
    *,
    page_type: str,
    fetch_ok: bool,
    http_status: int | None,
    partial: bool = False,
) -> dict[str, Any]:
    meta = extraction.get("meta") or {}
    headings = extraction.get("headings") or {}
    content = extraction.get("content") or {}
    links = extraction.get("links") or {}
    media = extraction.get("media") or {}
    structured = extraction.get("structured_data") or {}
    features = extraction.get("page_features") or {}
    trust = extraction.get("trust_signals") or {}
    derived = extraction.get("derived_metrics") or {}

    hero = content.get("hero") or {}
    struct = content.get("structural_features") or {}
    prec = content.get("precision_features") or {}
    answ = content.get("answerability_features") or {}

    title = (meta.get("title") or "").strip()
    desc = (meta.get("meta_description") or "").strip()
    h1_count = int(headings.get("h1_count") or 0)
    h2_count = int(struct.get("h2_count") or headings.get("h2_count") or 0)
    word_count = int(content.get("word_count") or 0)

    ctx = extraction.get("pipeline_context") or {}
    is_spa = ctx.get("is_probably_spa") is True
    fetch_method = str(ctx.get("primary_fetch_method") or "")
    pw_inconclusive = fetch_method == FETCH_METHOD_HTTP_PLAYWRIGHT_ATTEMPTED
    is_article = page_type == "article"

    internal_preview = int(links.get("internal_count") or 0)
    docs_editorial_like = _is_docs_editorial_like(
        extraction,
        page_type,
        word_count=word_count,
        h2_count=h2_count,
        internal_links_count=internal_preview,
    )

    issues: list[Issue] = []
    recommendations: list[Recommendation] = []
    strengths: list[str] = []

    # --- SEO: title + meta ---
    title_score = 100.0 if 15 <= len(title) <= 70 else (62.0 if title else 18.0)
    if len(title) > 70:
        issues.append(
            Issue(
                code="TITLE_LONG",
                title="Title tag may be truncated in SERPs",
                description="Long titles are often ellipsized; tighten to the primary topic.",
                severity="low",
                impact_scope="seo",
                evidence={"length": len(title)},
                fix_priority=3,
            )
        )
        recommendations.append(
            Recommendation(
                key="shorten-title",
                title="Shorten the page title for clearer SERP snippets",
                explanation="Aim for one clear value proposition in roughly 30–60 characters.",
                impact_scope="seo",
                priority=3,
                effort="low",
                expected_gain="Better snippet readability",
            )
        )
    elif title:
        strengths.append("Title tag present with a reasonable length")

    canonical = meta.get("canonical")
    og_title = meta.get("og_title")
    og_desc_raw = (str(meta.get("og_description") or "")).strip()
    social_bonus = 8.0 if (og_title or og_desc_raw) else 0.0
    twitter_card = bool(meta.get("twitter_card"))
    og_substitutes_meta = bool(len(og_desc_raw) >= 45)

    desc_score = 100.0 if 50 <= len(desc) <= 170 else (52.0 if desc else 14.0)
    if not desc:
        # Many modern sites rely on OG/Twitter for sharing; avoid harsh false positives
        if og_substitutes_meta or twitter_card:
            desc_score = 72.0
            strengths.append(
                "Open Graph / social card present (partial substitute when meta description is empty)"
            )
        else:
            issues.append(
                Issue(
                    code="META_DESC_MISSING",
                    title="Meta description missing or empty",
                    description="Snippets and GEO summaries benefit from a concise meta description.",
                    severity="medium",
                    impact_scope="seo",
                    evidence={},
                    fix_priority=2,
                )
            )
            recommendations.append(
                Recommendation(
                    key="add-meta-desc",
                    title="Add a unique meta description (about 120–160 characters)",
                    explanation="Summarize the page once in plain language for humans and systems.",
                    impact_scope="seo",
                    priority=2,
                    effort="low",
                    expected_gain="Improved snippet control",
                )
            )
    elif 50 <= len(desc) <= 170:
        strengths.append("Meta description present with useful length")

    tech_meta = 72.0
    if canonical:
        tech_meta += 14.0
        strengths.append("Canonical URL declared")
    tech_meta = _clamp(tech_meta + min(14.0, social_bonus))

    seo_title_meta = _clamp((title_score + desc_score + tech_meta) / 3.0)

    # --- SEO: headings ---
    h_score = 100.0 if h1_count == 1 else (68.0 if h1_count > 1 else 36.0)
    if h1_count == 0:
        issues.append(
            Issue(
                code="H1_MISSING",
                title="No H1 heading detected",
                description="A single clear H1 helps humans and parsers identify primary intent.",
                severity="medium",
                impact_scope="seo",
                evidence={"h1_count": h1_count},
                fix_priority=2,
            )
        )
        recommendations.append(
            Recommendation(
                key="IMPROVE_HEADING_STRUCTURE",
                title=_HEADING_RECO_TITLE,
                explanation=_HEADING_RECO_EXPL_H1,
                impact_scope="geo",
                priority=2,
                effort="low",
                expected_gain="Clearer topical focus and structure",
            )
        )
    elif h1_count > 1:
        if is_article:
            h_score = 82.0
            issues.append(
                Issue(
                    code="MULTIPLE_H1",
                    title="Multiple H1 headings detected",
                    description="Editorial or CMS layouts sometimes repeat H1s; consolidating still helps parsers.",
                    severity="low",
                    impact_scope="seo",
                    evidence={"h1_count": h1_count},
                    fix_priority=3,
                )
            )
            recommendations.append(
                Recommendation(
                    key="IMPROVE_HEADING_STRUCTURE",
                    title=_HEADING_RECO_TITLE,
                    explanation=_HEADING_RECO_EXPL_MULTI,
                    impact_scope="seo",
                    priority=3,
                    effort="low",
                    expected_gain="Clearer heading hierarchy",
                )
            )
        else:
            issues.append(
                Issue(
                    code="MULTIPLE_H1",
                    title="Multiple H1 headings detected",
                    description="Multiple H1s dilute primary-topic signals; prefer one H1 and H2 sections.",
                    severity="medium",
                    impact_scope="seo",
                    evidence={"h1_count": h1_count},
                    fix_priority=2,
                )
            )
            recommendations.append(
                Recommendation(
                    key="IMPROVE_HEADING_STRUCTURE",
                    title=_HEADING_RECO_TITLE,
                    explanation=_HEADING_RECO_EXPL_MULTI,
                    impact_scope="seo",
                    priority=2,
                    effort="low",
                    expected_gain="Clearer heading hierarchy",
                )
            )
    else:
        strengths.append("Single primary H1 detected")

    h2_long_threshold = 620 if is_article else 520
    if word_count > h2_long_threshold and h2_count < 2:
        issues.append(
            Issue(
                code="H2_MISSING_ON_LONG_PAGE",
                title="Long page with few H2 section headings",
                description="Section headings improve scanability and extractability for long content.",
                severity="medium",
                impact_scope="seo",
                evidence={"word_count": word_count, "h2_count": h2_count},
                fix_priority=2,
            )
        )
        recommendations.append(
            Recommendation(
                key="IMPROVE_HEADING_STRUCTURE",
                title=_HEADING_RECO_TITLE,
                explanation=_HEADING_RECO_EXPL_H2,
                impact_scope="geo",
                priority=2,
                effort="medium",
                expected_gain="Better scanability and GEO structure",
            )
        )
        h_score = min(h_score, 58.0)

    seo_heading_structure = h_score

    # --- SEO: content depth ---
    if word_count >= 900:
        depth = 100.0
    elif word_count >= 400:
        depth = 78.0
    elif word_count >= 200:
        depth = 55.0
    elif word_count >= 80:
        depth = 38.0
    else:
        depth = 22.0
    if word_count < 200:
        issues.append(
            Issue(
                code="CONTENT_THIN_SEO",
                title="Body copy is very short for substantive ranking signals",
                description="Thin pages offer limited evidence for relevance and topical depth.",
                severity="medium",
                impact_scope="seo",
                evidence={"word_count": word_count},
                fix_priority=2,
            )
        )
    seo_content_depth = depth

    # --- SEO: internal links ---
    internal = int(links.get("internal_count") or 0)
    descriptive = int(links.get("internal_with_descriptive_anchor_3plus_words") or 0)
    link_base = _clamp(min(100.0, internal * 12.0 + descriptive * 6.0))
    # cal-02: SPA / client routing often under-counts anchors; Playwright no-gain = fragile capture
    internal_thin_applies = word_count > 300 and internal < 2
    if internal_thin_applies and is_spa:
        link_base = max(link_base, 58.0)
    elif internal_thin_applies and pw_inconclusive and internal >= 1:
        link_base = max(link_base, 54.0)
    elif internal_thin_applies and pw_inconclusive:
        link_base = min(link_base, 56.0)
    elif internal_thin_applies:
        issues.append(
            Issue(
                code="INTERNAL_LINKS_THIN",
                title="Few internal links for a page of this size",
                description="Internal links help discovery and topical reinforcement.",
                severity="low",
                impact_scope="seo",
                evidence={"internal_count": internal, "word_count": word_count},
                fix_priority=3,
            )
        )
        recommendations.append(
            Recommendation(
                key="IMPROVE_INTERNAL_LINKING",
                title="Add relevant internal links with descriptive anchor text",
                explanation="Link to closely related pages using language that reflects the destination.",
                impact_scope="seo",
                priority=3,
                effort="low",
                expected_gain="Better crawl paths and context",
            )
        )
        link_base = min(link_base, 52.0)
    elif internal >= 5 and descriptive >= 2:
        strengths.append("Useful internal linking with descriptive anchors")

    seo_internal_links = link_base

    # --- SEO: technical viewport ---
    tech_score = 82.0 if features.get("has_viewport") else 54.0
    if not features.get("has_viewport"):
        issues.append(
            Issue(
                code="VIEWPORT_MISSING",
                title="Viewport meta tag not found",
                description="Mobile-friendly viewport helps rendering consistency and mobile SEO.",
                severity="medium",
                impact_scope="seo",
                evidence={},
                fix_priority=2,
            )
        )

    seo_scores_map = {
        "title_meta": seo_title_meta,
        "heading_structure": seo_heading_structure,
        "content_depth": seo_content_depth,
        "internal_links": seo_internal_links,
    }
    # blend viewport into title_meta bucket lightly (keeps 4 keys)
    seo_scores_map["title_meta"] = _clamp(seo_scores_map["title_meta"] * 0.88 + tech_score * 0.12)

    # --- GEO: hero ---
    hero_words = int(hero.get("approx_word_count") or 0)
    has_cta = bool(hero.get("has_cta_language"))
    hero_score = _clamp(28.0 + min(40.0, hero_words * 1.1) + (18.0 if has_cta else 0.0))
    commercial = page_type in ("landing_page", "homepage", "product_page", "pricing_page")
    commercial_geo = commercial and not docs_editorial_like
    if commercial_geo and hero_words < 22:
        issues.append(
            Issue(
                code="HERO_TOO_SHALLOW",
                title="Hero / above-the-fold copy looks thin",
                description="Key pages should state what this is, for whom, and the next step early.",
                severity="medium",
                impact_scope="geo",
                evidence={"hero_word_count": hero_words},
                fix_priority=2,
            )
        )
        recommendations.append(
            Recommendation(
                key="REWRITE_HERO",
                title="Clarify the hero: what it is, for whom, and the primary action",
                explanation="Expand the first visible block with a clear value proposition and CTA.",
                impact_scope="geo",
                priority=2,
                effort="medium",
                expected_gain="Higher clarity and extractability",
            )
        )
        hero_score = min(hero_score, 48.0)
    if commercial_geo and not has_cta and hero_words > 28:
        issues.append(
            Issue(
                code="HERO_CTA_WEAK",
                title="No obvious call-to-action language in the hero region",
                description="Action verbs (try, book, contact, sign up) help humans and agents infer intent.",
                severity="low",
                impact_scope="geo",
                evidence={},
                fix_priority=3,
            )
        )
        recommendations.append(
            Recommendation(
                key="REWRITE_HERO",
                title="Add a clear primary action in the hero",
                explanation="Use one obvious next step aligned with the page goal.",
                impact_scope="geo",
                priority=3,
                effort="low",
                expected_gain="Stronger conversion and intent signals",
            )
        )
    elif commercial_geo and hero_words >= 40 and has_cta:
        strengths.append("Hero region has substance and CTA language")

    geo_hero_clarity = hero_score

    # --- GEO: offer ---
    offer_hits = int(hero.get("offer_language_hits") or 0)
    offer_score = _clamp(40.0 + offer_hits * 18.0 + (12.0 if prec.get("currency_or_price_mentions") else 0.0))
    if commercial_geo and word_count > 250 and offer_hits == 0 and page_type != "article":
        issues.append(
            Issue(
                code="OFFER_TYPE_UNCLEAR",
                title="Offer or pricing signals are weak in the primary content",
                description="Commercial pages benefit from explicit offer, scope, or pricing language.",
                severity="medium",
                impact_scope="geo",
                evidence={"offer_language_hits": offer_hits},
                fix_priority=2,
            )
        )
        recommendations.append(
            Recommendation(
                key="CLARIFY_OFFER_POSITIONING",
                title="State what is sold, for whom, and how it is obtained",
                explanation="Clarify plan types, scope, or entry points so the page is easy to classify.",
                impact_scope="geo",
                priority=2,
                effort="medium",
                expected_gain="Clearer commercial understanding",
            )
        )
        offer_score = min(offer_score, 52.0)

    geo_offer_clarity = offer_score

    # --- GEO: extractability (lists, FAQ, questions) ---
    list_items = int((content.get("raw_metrics") or {}).get("list_item_count") or 0)
    faq_heur = bool(struct.get("has_faq_section_heuristic"))
    faq_schema = bool(answ.get("faq_schema_present"))
    how_heads = int(answ.get("how_what_why_heading_count") or 0)
    qmarks = int(answ.get("question_marks_in_body") or 0)

    ext_score = _clamp(
        32.0
        + min(28.0, list_items * 1.2)
        + (18.0 if faq_heur else 0.0)
        + (14.0 if faq_schema else 0.0)
        + min(22.0, how_heads * 7.0)
        + min(16.0, qmarks * 1.5)
    )
    # cal-02: longform articles tolerate less FAQ-shaped structure (provisional floors)
    faq_word_floor = 620 if is_article else 450
    if (
        word_count > faq_word_floor
        and not faq_heur
        and not faq_schema
        and how_heads < 1
        and qmarks < 2
    ):
        issues.append(
            Issue(
                code="FAQ_ANSWERABILITY_WEAK",
                title="Limited FAQ / Q&A style structure for a long page",
                description="Question-shaped headings and short answers improve extractability.",
                severity="low",
                impact_scope="geo",
                evidence={"word_count": word_count},
                fix_priority=3,
            )
        )
        recommendations.append(
            Recommendation(
                key="ADD_FAQ_OR_QA_BLOCK",
                title="Add a small FAQ or Q&A block for common questions",
                explanation="Use real user questions; keep answers concise and factual.",
                impact_scope="geo",
                priority=3,
                effort="medium",
                expected_gain="Better answer surfaces and citations",
            )
        )
        ext_score = min(ext_score, 55.0)
    elif faq_heur or faq_schema:
        strengths.append("FAQ-style structure or FAQ schema detected")

    geo_extractability = ext_score

    # --- GEO: citation readiness ---
    cit_idx = float(derived.get("citation_readiness_index") or 0.0)
    ex_hits = int(prec.get("example_phrase_hits") or 0)
    step_hits = int(prec.get("step_language_hits") or 0)
    years = int(prec.get("year_mentions") or 0)
    cit_score = _clamp(cit_idx * 0.55 + min(40.0, (ex_hits + step_hits) * 10.0) + min(15.0, years * 3.0))
    # cal-02: lists + sections + length often carry implicit “evidence” on articles (provisional)
    citation_relaxed = (
        is_article
        and word_count >= 550
        and list_items >= 8
        and h2_count >= 2
    )
    if word_count > 320 and cit_idx < 28 and ex_hits == 0 and not citation_relaxed:
        issues.append(
            Issue(
                code="CITATION_SIGNALS_WEAK",
                title="Few concrete examples, steps, or quantified facts",
                description="Examples and specifics make content easier to cite and trust.",
                severity="low",
                impact_scope="geo",
                evidence={"citation_readiness_index": cit_idx},
                fix_priority=3,
            )
        )
        recommendations.append(
            Recommendation(
                key="ADD_CONCRETE_EXAMPLES",
                title="Add specific examples, steps, or numbers where relevant",
                explanation="Short illustrations and metrics improve citation readiness.",
                impact_scope="geo",
                priority=3,
                effort="medium",
                expected_gain="Richer evidence for models and users",
            )
        )

    geo_citation_readiness = cit_score

    # --- GEO: trust / entity ---
    json_ld = int(structured.get("json_ld_scripts") or 0)
    org_like = bool(trust.get("has_organization_like_schema"))
    trust_score = _clamp(
        38.0
        + (22.0 if json_ld > 0 else 0.0)
        + (16.0 if org_like else 0.0)
        + min(12.0, int(trust.get("contact_mailto_count") or 0) * 6.0)
        + min(12.0, int(trust.get("contact_tel_count") or 0) * 6.0)
        + (10.0 if trust.get("privacy_policy_signal") else 0.0)
    )
    if word_count > 400 and json_ld == 0:
        issues.append(
            Issue(
                code="SCHEMA_JSONLD_MISSING",
                title="No JSON-LD structured data detected",
                description="Structured data helps search systems understand entities and page type.",
                severity="low",
                impact_scope="seo",
                evidence={},
                fix_priority=3,
            )
        )
        recommendations.append(
            Recommendation(
                key="ADD_STRUCTURED_DATA_JSONLD",
                title="Add appropriate JSON-LD (WebSite, Organization, or Article)",
                explanation="Start with schema.org types that match the page; validate with Rich Results.",
                impact_scope="seo",
                priority=3,
                effort="medium",
                expected_gain="Clearer machine-readable semantics",
            )
        )
    elif json_ld > 0:
        strengths.append("JSON-LD structured data present")

    thin_trust = not org_like and int(trust.get("contact_mailto_count") or 0) == 0 and not trust.get(
        "privacy_policy_signal"
    )
    if word_count > 350 and thin_trust and page_type in ("homepage", "landing_page", "about_page"):
        issues.append(
            Issue(
                code="TRUST_LAYER_THIN",
                title="Light trust signals (entity, contact, or policy)",
                description="Home and marketing pages benefit from visible entity and policy paths.",
                severity="low",
                impact_scope="geo",
                evidence={},
                fix_priority=4,
            )
        )
        recommendations.append(
            Recommendation(
                key="STRENGTHEN_TRUST_SIGNALS",
                title="Surface organization identity and policy/contact paths",
                explanation="Link contact, privacy, or about content; add Organization schema when relevant.",
                impact_scope="geo",
                priority=4,
                effort="low",
                expected_gain="Stronger entity and trust cues",
            )
        )

    geo_trust_entity = trust_score

    # --- Media alt (cross-cutting, nudge GEO media subscore via trust_entity coupling) ---
    img_n = int(media.get("image_count") or 0)
    alt_ratio = float(media.get("images_alt_ratio") or 0.0)
    if img_n >= 6 and alt_ratio < 0.30:
        issues.append(
            Issue(
                code="IMAGES_ALT_WEAK",
                title="Several images lack useful alt text",
                description="Alt text improves accessibility and image understanding.",
                severity="low",
                impact_scope="seo",
                evidence={"image_count": img_n, "images_alt_ratio": alt_ratio},
                fix_priority=3,
            )
        )
        recommendations.append(
            Recommendation(
                key="IMPROVE_IMAGE_ALT",
                title="Add concise descriptive alt text to informative images",
                explanation="Describe what matters in the image; leave decorative images empty with role=presentation if appropriate.",
                impact_scope="seo",
                priority=3,
                effort="low",
                expected_gain="Accessibility and richer media signals",
            )
        )
        geo_trust_entity = min(geo_trust_entity, 62.0)

    geo_scores_map = {
        "hero_clarity": geo_hero_clarity,
        "offer_clarity": geo_offer_clarity,
        "extractability": geo_extractability,
        "citation_readiness": geo_citation_readiness,
        "trust_entity": geo_trust_entity,
    }

    if partial:
        for gk in list(geo_scores_map.keys()):
            geo_scores_map[gk] = _clamp(geo_scores_map[gk] * 0.96)

    seo_w, geo_w = _page_type_weights(page_type)
    seo_score = _weighted_avg(seo_scores_map, seo_w)
    geo_score = _weighted_avg(geo_scores_map, geo_w)
    if partial and (word_count < 400 or is_spa):
        geo_score = min(geo_score, 77.0)
    global_score = _clamp(0.5 * seo_score + 0.5 * geo_score)

    seo_sub = {k: round(v, 1) for k, v in seo_scores_map.items()}
    geo_sub = {k: round(v, 1) for k, v in geo_scores_map.items()}

    limitations: list[Limitation] = []
    if not fetch_ok or (http_status and http_status >= 400):
        limitations.append(
            Limitation(
                code="FETCH_DEGRADED",
                message="Fetch was incomplete or returned an error status; scores are indicative only.",
                severity="warning",
            )
        )
    if partial:
        limitations.append(
            Limitation(
                code="PARTIAL_PIPELINE",
                message="Analysis used partial or degraded page capture (thin HTML, fetch limits, or bot defenses).",
                severity="warning",
            )
        )
    if word_count < 150:
        limitations.append(
            Limitation(
                code="THIN_PAGE",
                message="Low word count — GEO and SEO signals have limited evidence.",
                severity="warning",
            )
        )

    ext_limits = extraction.get("limitations") or []
    for row in ext_limits:
        if isinstance(row, dict) and row.get("message"):
            limitations.append(
                Limitation(
                    code=str(row.get("code", "EXTRACTION")),
                    message=str(row["message"]),
                    severity=str(row.get("severity", "info")),
                )
            )

    conf_numeric = 0.86
    if not fetch_ok:
        conf_numeric -= 0.25
    if http_status and http_status != 200:
        conf_numeric -= 0.14
    if partial:
        conf_numeric -= 0.12
    if word_count < 200:
        conf_numeric -= 0.09
    if not json_ld and word_count > 450:
        conf_numeric -= 0.04
    if partial and is_spa:
        conf_numeric -= 0.05
    if partial and (word_count < 400 or is_spa):
        conf_numeric = min(conf_numeric, 0.68)
    conf_numeric = _clamp(conf_numeric, 0.2, 1.0)

    if conf_numeric >= 0.7:
        conf_label = AnalysisConfidence.HIGH.value
    elif conf_numeric >= 0.45:
        conf_label = AnalysisConfidence.MEDIUM.value
    else:
        conf_label = AnalysisConfidence.LOW.value

    issues.sort(key=lambda i: (i.fix_priority or 99, i.severity or "z"))
    recommendations = _dedupe_recommendations(recommendations)
    recommendations = _merge_hero_offer_recommendations(recommendations)
    recommendations = _cap_recommendation_list(recommendations, 6)

    summary_parts = [
        f"Page type context: {page_type}.",
        f"SEO {seo_score:.0f}/100 · GEO {geo_score:.0f}/100 (global {global_score:.0f}/100).",
    ]
    if issues:
        summary_parts.append(f"Priority: {issues[0].title.lower()}.")
    summary = " ".join(summary_parts)

    return {
        "scoring_version": SCORING_VERSION,
        "ruleset_version": RULESET_VERSION,
        "global_score": round(global_score, 2),
        "seo_score": round(seo_score, 2),
        "geo_score": round(geo_score, 2),
        "seo_subscores": seo_sub,
        "geo_subscores": geo_sub,
        "penalties": {},
        "bonuses": {},
        "confidence_score": round(conf_numeric, 4),
        "analysis_confidence": conf_label,
        "issues": issues,
        "recommendations": recommendations,
        "limitations": limitations,
        "strengths": strengths,
        "summary": summary,
    }
