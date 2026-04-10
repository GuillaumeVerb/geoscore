"""Regression tests for calibration-related scoring tweaks (og:description substitute, thresholds)."""

from __future__ import annotations

from app.services.pipeline.score_minimal import run_deterministic_score


def _minimal_extraction(**overrides: object) -> dict:
    base: dict = {
        "meta": {
            "title": "A reasonable page title for testing",
            "meta_description": "x" * 120,
            "canonical": "https://example.com/",
            "og_title": "OG",
            "og_description": "y" * 50,
        },
        "headings": {"h1_count": 1, "h2": [], "h3": []},
        "content": {
            "word_count": 500,
            "hero": {"approx_word_count": 80, "has_cta_language": True, "offer_language_hits": 2},
            "structural_features": {"h2_count": 4, "has_faq_section_heuristic": True},
            "raw_metrics": {"list_item_count": 8},
            "precision_features": {"example_phrase_hits": 2, "step_language_hits": 0, "currency_or_price_mentions": 1},
            "answerability_features": {"faq_schema_present": False, "how_what_why_heading_count": 1, "question_marks_in_body": 2},
        },
        "links": {"internal_count": 6, "internal_with_descriptive_anchor_3plus_words": 3, "external_count": 2},
        "media": {"image_count": 2, "images_alt_ratio": 0.5},
        "structured_data": {"json_ld_scripts": 1},
        "page_features": {"has_viewport": True},
        "trust_signals": {
            "has_organization_like_schema": True,
            "contact_mailto_count": 0,
            "privacy_policy_signal": True,
        },
        "derived_metrics": {"citation_readiness_index": 50.0},
        "limitations": [],
    }
    for k, v in overrides.items():
        base[k] = v
    return base


def test_og_description_substitutes_missing_meta_description() -> None:
    m = _minimal_extraction()
    m["meta"] = {
        "title": "Product home",
        "meta_description": "",
        "og_description": "A" * 50,
        "og_title": "Product",
    }
    out = run_deterministic_score(m, page_type="homepage", fetch_ok=True, http_status=200, partial=False)
    codes = {i.code for i in out["issues"]}
    assert "META_DESC_MISSING" not in codes
    assert any("Open Graph" in s for s in out["strengths"])


def test_meta_missing_still_fires_without_og() -> None:
    m = _minimal_extraction()
    m["meta"] = {"title": "Only title", "meta_description": ""}
    out = run_deterministic_score(m, page_type="homepage", fetch_ok=True, http_status=200, partial=False)
    assert any(i.code == "META_DESC_MISSING" for i in out["issues"])


def test_internal_links_thin_suppressed_when_spa() -> None:
    m = _minimal_extraction()
    m["content"]["word_count"] = 400
    m["links"] = {"internal_count": 0, "internal_with_descriptive_anchor_3plus_words": 0, "external_count": 1}
    m["pipeline_context"] = {"is_probably_spa": True, "primary_fetch_method": "http_get"}
    out = run_deterministic_score(m, page_type="homepage", fetch_ok=True, http_status=200, partial=False)
    assert "INTERNAL_LINKS_THIN" not in {i.code for i in out["issues"]}


def test_article_multiple_h1_is_low_severity() -> None:
    m = _minimal_extraction()
    m["headings"]["h1_count"] = 2
    out = run_deterministic_score(m, page_type="article", fetch_ok=True, http_status=200, partial=False)
    multi = [i for i in out["issues"] if i.code == "MULTIPLE_H1"]
    assert len(multi) == 1
    assert multi[0].severity == "low"


def test_partial_sparse_capture_not_high_confidence() -> None:
    m = _minimal_extraction()
    m["content"]["word_count"] = 250
    out = run_deterministic_score(
        m,
        page_type="homepage",
        fetch_ok=True,
        http_status=200,
        partial=True,
    )
    assert out["analysis_confidence"] != "high"


def test_partial_spa_caps_confidence_and_geo() -> None:
    m = _minimal_extraction()
    m["pipeline_context"] = {"is_probably_spa": True, "primary_fetch_method": "http_playwright_attempted"}
    out = run_deterministic_score(
        m,
        page_type="homepage",
        fetch_ok=True,
        http_status=200,
        partial=True,
    )
    assert out["analysis_confidence"] != "high"
    assert out["geo_score"] <= 77.0


def test_rewrite_hero_and_offer_merge_when_both_fire() -> None:
    m = _minimal_extraction()
    m["content"]["word_count"] = 400
    m["content"]["hero"] = {
        "approx_word_count": 10,
        "has_cta_language": False,
        "offer_language_hits": 0,
    }
    m["content"]["precision_features"] = {"currency_or_price_mentions": False}
    out = run_deterministic_score(
        m,
        page_type="landing_page",
        fetch_ok=True,
        http_status=200,
        partial=False,
    )
    keys = [r.key for r in out["recommendations"] if r.key]
    assert "REWRITE_HERO" not in keys
    assert "CLARIFY_OFFER_POSITIONING" not in keys
    assert "ABOVE_FOLD_CLARITY" in keys


def test_docs_editorial_like_suppresses_commercial_hero_offer() -> None:
    """cal-03: react.dev-style doc home should not get commercial GEO nags."""
    m = _minimal_extraction()
    m["url_info"] = {"normalized_url": "https://react.dev/"}
    m["headings"]["h1_count"] = 2
    m["content"]["word_count"] = 1500
    m["content"]["structural_features"] = {"h2_count": 15, "has_faq_section_heuristic": True}
    m["content"]["hero"] = {
        "approx_word_count": 8,
        "has_cta_language": False,
        "offer_language_hits": 0,
    }
    m["content"]["precision_features"] = {
        "example_phrase_hits": 0,
        "step_language_hits": 0,
        "currency_or_price_mentions": False,
    }
    m["links"] = {"internal_count": 35, "internal_with_descriptive_anchor_3plus_words": 10, "external_count": 2}
    out = run_deterministic_score(m, page_type="homepage", fetch_ok=True, http_status=200, partial=False)
    codes = {i.code for i in out["issues"]}
    keys = {r.key for r in out["recommendations"] if r.key}
    assert "OFFER_TYPE_UNCLEAR" not in codes
    assert "HERO_CTA_WEAK" not in codes
    assert "HERO_TOO_SHALLOW" not in codes
    assert "ABOVE_FOLD_CLARITY" not in keys
    assert "MULTIPLE_H1" in codes


def test_normal_homepage_still_triggers_commercial_geo_issues() -> None:
    m = _minimal_extraction()
    m["url_info"] = {"normalized_url": "https://example.com/"}
    m["content"]["word_count"] = 400
    m["content"]["hero"] = {
        "approx_word_count": 10,
        "has_cta_language": False,
        "offer_language_hits": 0,
    }
    m["content"]["precision_features"] = {"currency_or_price_mentions": False}
    out = run_deterministic_score(m, page_type="homepage", fetch_ok=True, http_status=200, partial=False)
    codes = {i.code for i in out["issues"]}
    assert "OFFER_TYPE_UNCLEAR" in codes
    assert "HERO_TOO_SHALLOW" in codes


def test_docs_path_prefix_suppresses_offer() -> None:
    m = _minimal_extraction()
    m["url_info"] = {"normalized_url": "https://acme.com/docs/install"}
    m["content"]["word_count"] = 600
    m["content"]["hero"] = {
        "approx_word_count": 5,
        "has_cta_language": False,
        "offer_language_hits": 0,
    }
    m["content"]["precision_features"] = {"currency_or_price_mentions": False}
    out = run_deterministic_score(m, page_type="homepage", fetch_ok=True, http_status=200, partial=False)
    assert "OFFER_TYPE_UNCLEAR" not in {i.code for i in out["issues"]}


def test_article_longform_skips_citation_weak_when_structured() -> None:
    m = _minimal_extraction()
    m["headings"]["h1_count"] = 1
    m["content"]["word_count"] = 600
    m["content"]["structural_features"] = {"h2_count": 4, "has_faq_section_heuristic": True}
    m["content"]["raw_metrics"] = {"list_item_count": 10}
    m["content"]["precision_features"] = {
        "example_phrase_hits": 0,
        "step_language_hits": 0,
        "currency_or_price_mentions": 0,
    }
    m["derived_metrics"] = {"citation_readiness_index": 10.0}
    out = run_deterministic_score(m, page_type="article", fetch_ok=True, http_status=200, partial=False)
    assert "CITATION_SIGNALS_WEAK" not in {i.code for i in out["issues"]}
