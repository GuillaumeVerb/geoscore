"""Unit tests for rich extraction + deterministic scoring (no HTTP server)."""

from __future__ import annotations

from uuid import uuid4

from app.services.pipeline.extract_step import build_extraction_payload
from app.services.pipeline.score_minimal import run_deterministic_score

_META_DESC = ("Track funnels and retention. " * 8).strip()
_BODY_WORDS = "word " * 400

SAMPLE_HTML = f"""
<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Product analytics for growing teams today</title>
<meta name="description" content="{_META_DESC}"/>
<link rel="canonical" href="https://example.com/product"/>
<meta property="og:title" content="Product analytics"/>
<meta property="og:description" content="Grow faster"/>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Organization","name":"Acme Inc"}}
</script>
</head><body>
<main>
<h1>Analytics your team will actually use</h1>
<p class="hero">Sign up free and see dashboards in minutes. Start your trial today.</p>
<p>{_BODY_WORDS}</p>
<h2>Pricing</h2><p>Plans from $29 per month with annual billing.</p>
<h2>FAQ</h2><p>What is included? Everything in the starter tier.</p>
<ul><li>Feature one</li><li>Feature two</li><li>Feature three</li></ul>
<img src="/a.png" alt="Dashboard screenshot"/>
<img src="/b.png" alt=""/>
</main>
<footer><a href="/privacy">Privacy policy</a> · <a href="mailto:hi@example.com">Contact</a></footer>
</body></html>
"""


def test_extraction_nested_sections() -> None:
    sid = uuid4()
    payload = build_extraction_payload(
        sid,
        "https://example.com/product",
        fetch_info={"ok": True},
        render_info={"engine": "none"},
        html=SAMPLE_HTML,
    )
    assert "raw_metrics" in payload["content"]
    assert "hero" in payload["content"]
    assert "structural_features" in payload["content"]
    assert payload["content"]["answerability_features"]["faq_schema_present"] is False
    assert payload["structured_data"]["json_ld_scripts"] >= 1
    assert "Organization" in (payload["structured_data"]["schema_types_found"] or [])
    assert payload["meta"].get("html_lang") == "en"
    assert payload["derived_metrics"].get("extractability_index", 0) > 0


def test_scoring_returns_catalog_style_issues() -> None:
    sid = uuid4()
    ext = build_extraction_payload(
        sid,
        "https://example.com/p",
        {},
        {},
        html=SAMPLE_HTML,
    )
    out = run_deterministic_score(
        ext,
        page_type="product_page",
        fetch_ok=True,
        http_status=200,
        partial=False,
    )
    assert 0 <= out["global_score"] <= 100
    codes = {i.code for i in out["issues"]}
    assert ext["content"]["word_count"] > 200
    assert "CONTENT_THIN_SEO" not in codes
    keys = {r.key for r in out["recommendations"] if r.key}
    assert len(keys) == len([r for r in out["recommendations"] if r.key])
    assert "seo_subscores" in out and "geo_subscores" in out
    assert set(out["seo_subscores"]) >= {"title_meta", "heading_structure", "content_depth", "internal_links"}
    assert set(out["geo_subscores"]) >= {
        "hero_clarity",
        "offer_clarity",
        "extractability",
        "citation_readiness",
        "trust_entity",
    }
