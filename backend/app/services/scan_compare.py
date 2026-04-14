"""Presentation-only compare between two scan payloads (no scoring delta engine)."""

from __future__ import annotations

from app.schemas.api_contracts import ScanCompareResponse, ScanCompareScores, ScanDetailResponse
from app.schemas.recommendation import Recommendation


def _rec_identity(r: Recommendation) -> str:
    if r.key and str(r.key).strip():
        return f"key:{str(r.key).strip().lower()}"
    return f"title:{(r.title or '').strip().lower()}"


def build_scan_compare(parent: ScanDetailResponse, child: ScanDetailResponse) -> ScanCompareResponse:
    """Parent = earlier run; child = newer run (e.g. rescan). Diff issues by code, recs by key/title."""
    pb = {i.code: i for i in parent.issues}
    cb = {i.code: i for i in child.issues}
    resolved_issues = [pb[c] for c in pb if c not in cb]
    new_issues = [cb[c] for c in cb if c not in pb]

    pr = {_rec_identity(r): r for r in parent.recommendations}
    cr = {_rec_identity(r): r for r in child.recommendations}
    rec_removed = [pr[k] for k in pr if k not in cr]
    rec_new = [cr[k] for k in cr if k not in pr]
    rec_persistent = [cr[k] for k in cr if k in pr]

    before_scores = ScanCompareScores(
        global_score=parent.global_score,
        seo_score=parent.seo_score,
        geo_score=parent.geo_score,
    )
    after_scores = ScanCompareScores(
        global_score=child.global_score,
        seo_score=child.seo_score,
        geo_score=child.geo_score,
    )

    submitted = str(child.meta.get("submitted_url") or parent.meta.get("submitted_url") or "")

    return ScanCompareResponse(
        parent_scan_id=parent.scan_id,
        child_scan_id=child.scan_id,
        submitted_url=submitted,
        before_scores=before_scores,
        after_scores=after_scores,
        resolved_issues=resolved_issues,
        new_issues=new_issues,
        recommendations_persistent=rec_persistent,
        recommendations_new=rec_new,
        recommendations_removed=rec_removed,
    )
