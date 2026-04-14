"""Presentation-only scan compare (no scoring engine)."""

from __future__ import annotations

import uuid

from app.domain.enums import ScanStatus
from app.schemas.api_contracts import ScanDetailResponse
from app.schemas.issue import Issue
from app.schemas.recommendation import Recommendation
from app.services.scan_compare import build_scan_compare


def _detail(
    scan_id: uuid.UUID,
    *,
    issues: list[Issue],
    recs: list[Recommendation],
    global_score: float | None = 50.0,
    seo_score: float | None = 40.0,
    geo_score: float | None = 30.0,
    meta: dict | None = None,
) -> ScanDetailResponse:
    return ScanDetailResponse(
        scan_id=scan_id,
        status=ScanStatus.COMPLETED,
        global_score=global_score,
        seo_score=seo_score,
        geo_score=geo_score,
        issues=issues,
        recommendations=recs,
        meta=meta or {},
    )


def test_build_scan_compare_issues_and_recommendations() -> None:
    pid = uuid.uuid4()
    cid = uuid.uuid4()
    parent = _detail(
        pid,
        issues=[
            Issue(code="gone", title="Removed issue"),
            Issue(code="stays", title="Still here"),
        ],
        recs=[
            Recommendation(key="a", title="Rec A"),
            Recommendation(key="b", title="Rec B"),
        ],
        global_score=10.0,
        seo_score=20.0,
        geo_score=30.0,
        meta={"submitted_url": "https://example.com/page"},
    )
    child = _detail(
        cid,
        issues=[
            Issue(code="stays", title="Still here"),
            Issue(code="fresh", title="New issue"),
        ],
        recs=[
            Recommendation(key="a", title="Rec A"),
            Recommendation(key="c", title="Rec C"),
        ],
        global_score=15.0,
        seo_score=25.0,
        geo_score=35.0,
        meta={"submitted_url": "https://example.com/page"},
    )

    out = build_scan_compare(parent, child)

    assert out.parent_scan_id == pid
    assert out.child_scan_id == cid
    assert out.submitted_url == "https://example.com/page"
    assert out.before_scores.global_score == 10.0
    assert out.after_scores.geo_score == 35.0

    assert [i.code for i in out.resolved_issues] == ["gone"]
    assert [i.code for i in out.new_issues] == ["fresh"]

    assert len(out.recommendations_persistent) == 1
    assert out.recommendations_persistent[0].key == "a"
    assert len(out.recommendations_new) == 1
    assert out.recommendations_new[0].key == "c"
    assert len(out.recommendations_removed) == 1
    assert out.recommendations_removed[0].key == "b"
