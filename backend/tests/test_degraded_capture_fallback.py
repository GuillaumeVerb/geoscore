"""Product-layer fallbacks for partial scans with sparse issues/recommendations."""

from __future__ import annotations

from app.schemas.issue import Issue
from app.schemas.limitation import Limitation
from app.schemas.recommendation import Recommendation
from app.services.degraded_capture_fallback import enrich_score_bundle_for_degraded_capture


def _bundle(
    *,
    issues: list[Issue],
    recs: list[Recommendation],
    limitations: list[Limitation],
) -> dict:
    return {
        "issues": issues,
        "recommendations": recs,
        "limitations": limitations,
        "global_score": 60.0,
        "seo_score": 60.0,
        "geo_score": 60.0,
    }


def test_adds_diagnostic_when_partial_strong_limits_sparse_outputs() -> None:
    b = _bundle(
        issues=[],
        recs=[],
        limitations=[
            Limitation(code="FETCH_DEGRADED", message="bad", severity="warning"),
            Limitation(code="PARTIAL_PIPELINE", message="partial", severity="warning"),
        ],
    )
    enrich_score_bundle_for_degraded_capture(b, is_partial=True, pipeline_context=None)
    codes = {i.code for i in b["issues"]}
    keys = {r.key for r in b["recommendations"] if r.key}
    assert "CAPTURE_QUALITY_DEGRADED" in codes
    assert "IMPROVE_CAPTURE_OR_RETRY" in keys
    assert b["global_score"] == 60.0


def test_noop_when_completed() -> None:
    b = _bundle(issues=[], recs=[], limitations=[Limitation(code="FETCH_DEGRADED", message="x", severity="warning")])
    enrich_score_bundle_for_degraded_capture(b, is_partial=False, pipeline_context=None)
    assert b["issues"] == []


def test_noop_when_many_issues_already() -> None:
    b = _bundle(
        issues=[
            Issue(code="A", title="a", severity="low", impact_scope="seo", fix_priority=3),
            Issue(code="B", title="b", severity="low", impact_scope="seo", fix_priority=3),
        ],
        recs=[],
        limitations=[Limitation(code="FETCH_DEGRADED", message="x", severity="warning")],
    )
    enrich_score_bundle_for_degraded_capture(b, is_partial=True, pipeline_context=None)
    assert not any(i.code == "CAPTURE_QUALITY_DEGRADED" for i in b["issues"])


def test_thin_spa_many_issues_appends_visible_reco_only() -> None:
    b = _bundle(
        issues=[
            Issue(code="META_DESC_MISSING", title="m", severity="low", impact_scope="seo", fix_priority=3),
            Issue(code="CONTENT_THIN_SEO", title="c", severity="low", impact_scope="seo", fix_priority=3),
        ],
        recs=[],
        limitations=[Limitation(code="THIN_PAGE", message="thin", severity="warning")],
    )
    enrich_score_bundle_for_degraded_capture(
        b,
        is_partial=True,
        pipeline_context={"is_probably_spa": True},
    )
    keys = [r.key for r in b["recommendations"] if r.key]
    assert "VISIBLE_CONTENT_MAY_BE_INCOMPLETE" in keys
    assert "CAPTURE_QUALITY_DEGRADED" not in {i.code for i in b["issues"]}


def test_playwright_failed_adds_install_hint() -> None:
    b = _bundle(
        issues=[],
        recs=[],
        limitations=[
            Limitation(code="PARTIAL_PIPELINE", message="p", severity="warning"),
            Limitation(code="PLAYWRIGHT_FAILED", message="boom", severity="warning"),
        ],
    )
    enrich_score_bundle_for_degraded_capture(b, is_partial=True, pipeline_context=None)
    rec = next(r for r in b["recommendations"] if r.key == "IMPROVE_CAPTURE_OR_RETRY")
    assert "Playwright" in rec.explanation or "playwright" in rec.explanation.lower()
