"""Smoke: deterministic score bundle shape from a minimal extraction (no DB, no fetch)."""

from __future__ import annotations

from app.services.pipeline.score_minimal import run_deterministic_score


def test_deterministic_score_returns_bounded_global() -> None:
    extraction: dict = {
        "meta": {
            "title": "Example product",
            "meta_description": "d" * 120,
        },
        "headings": {"h1_count": 1, "h2": [], "h3": []},
        "content": {
            "word_count": 400,
            "hero": {"approx_word_count": 40, "has_cta_language": True, "offer_language_hits": 1},
            "structural_features": {"h2_count": 2},
            "raw_metrics": {"list_item_count": 4},
            "precision_features": {"example_phrase_hits": 0, "step_language_hits": 0, "currency_or_price_mentions": 0},
            "answerability_features": {"faq_schema_present": False, "how_what_why_heading_count": 0, "question_marks_in_body": 0},
        },
        "links": {"internal_count": 3, "internal_with_descriptive_anchor_3plus_words": 1, "external_count": 1},
        "media": {"image_count": 1, "images_alt_ratio": 0.4},
        "structured_data": {"json_ld_scripts": 0},
        "page_features": {"has_viewport": True},
        "trust_signals": {"has_organization_like_schema": False, "contact_mailto_count": 0, "privacy_policy_signal": False},
        "derived_metrics": {"citation_readiness_index": 40.0},
        "limitations": [],
    }
    out = run_deterministic_score(
        extraction,
        page_type="landing_page",
        fetch_ok=True,
        http_status=200,
        partial=False,
    )
    g = float(out["global_score"])
    assert 0.0 <= g <= 100.0
    assert out.get("analysis_confidence")
    assert isinstance(out.get("issues"), list)
    assert isinstance(out.get("recommendations"), list)
