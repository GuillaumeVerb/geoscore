"""Assemble ScanDetailResponse / PublicReportResponse from persisted rows."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.domain.enums import AnalysisConfidence, PageType, ScanStatus
from app.models.public_report import PublicReport
from app.models.scan import Scan
from app.models.scan_extraction import ScanExtraction
from app.models.scan_issue import ScanIssue
from app.models.scan_recommendation import ScanRecommendation
from app.models.scan_score import ScanScore
from app.schemas.api_contracts import PublicReportResponse, ScanDetailResponse, ScanSummaryItem
from app.schemas.extraction import ExtractionSchema
from app.schemas.issue import Issue
from app.schemas.limitation import Limitation
from app.schemas.recommendation import Recommendation
from app.schemas.score import ScoreBlock


def _parse_page_type(value: str | None) -> PageType | None:
    if value is None:
        return None
    try:
        return PageType(value)
    except ValueError:
        return PageType.OTHER


def _parse_confidence(value: str | None) -> AnalysisConfidence | None:
    if value is None:
        return None
    try:
        return AnalysisConfidence(value)
    except ValueError:
        return AnalysisConfidence.UNKNOWN


def _parse_scan_status(value: str) -> ScanStatus:
    try:
        return ScanStatus(value)
    except ValueError:
        return ScanStatus.QUEUED


def list_scan_summaries(
    db: Session, *, user_id: UUID, limit: int = 40, project_id: UUID | None = None
) -> list[ScanSummaryItem]:
    """Newest scans first for this user; scores from latest ScanScore row per scan."""
    q = select(Scan).where(Scan.user_id == user_id)
    if project_id is not None:
        q = q.where(Scan.project_id == project_id)
    scans = db.scalars(q.order_by(desc(Scan.created_at)).limit(limit)).all()
    out: list[ScanSummaryItem] = []
    for scan in scans:
        score_row = (
            db.execute(
                select(ScanScore)
                .where(ScanScore.scan_id == scan.id)
                .order_by(desc(ScanScore.created_at))
                .limit(1)
            )
            .scalars()
            .first()
        )
        global_score = float(score_row.global_score) if score_row and score_row.global_score is not None else None
        seo_score = float(score_row.seo_score) if score_row and score_row.seo_score is not None else None
        geo_score = float(score_row.geo_score) if score_row and score_row.geo_score is not None else None
        out.append(
            ScanSummaryItem(
                scan_id=scan.id,
                status=_parse_scan_status(scan.status),
                submitted_url=scan.submitted_url,
                domain=scan.domain,
                page_type_detected=_parse_page_type(scan.page_type_detected),
                page_type_final=_parse_page_type(scan.page_type_final),
                analysis_confidence=_parse_confidence(scan.analysis_confidence),
                global_score=global_score,
                seo_score=seo_score,
                geo_score=geo_score,
                created_at=scan.created_at,
                completed_at=scan.completed_at,
                project_id=scan.project_id,
                parent_scan_id=scan.parent_scan_id,
            )
        )
    return out


def scan_to_detail_response(db: Session, scan_id: UUID) -> ScanDetailResponse | None:
    scan = db.get(Scan, scan_id)
    if scan is None:
        return None

    extraction_model = None
    ext = (
        db.execute(
            select(ScanExtraction)
            .where(ScanExtraction.scan_id == scan.id)
            .order_by(ScanExtraction.created_at.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )
    if ext and ext.extraction_payload:
        try:
            extraction_model = ExtractionSchema.model_validate(ext.extraction_payload)
        except Exception:
            extraction_model = None

    score_row = (
        db.execute(
            select(ScanScore).where(ScanScore.scan_id == scan.id).order_by(ScanScore.created_at.desc()).limit(1)
        )
        .scalars()
        .first()
    )
    scores = None
    global_score = None
    seo_score = None
    geo_score = None
    if score_row:
        global_score = float(score_row.global_score)
        seo_score = float(score_row.seo_score)
        geo_score = float(score_row.geo_score)
        scores = ScoreBlock(
            global_score=global_score,
            seo_score=seo_score,
            geo_score=geo_score,
            seo_subscores=dict(score_row.seo_subscores or {}),
            geo_subscores=dict(score_row.geo_subscores or {}),
            penalties=dict(score_row.penalties or {}),
            bonuses=dict(score_row.bonuses or {}),
            confidence_score=float(score_row.confidence_score)
            if score_row.confidence_score is not None
            else None,
        )

    issue_rows = (
        db.execute(select(ScanIssue).where(ScanIssue.scan_id == scan.id).order_by(ScanIssue.fix_priority.asc()))
        .scalars()
        .all()
    )
    issues = [
        Issue(
            code=r.code,
            title=r.title,
            description=r.description,
            severity=r.severity,
            impact_scope=r.impact_scope,
            evidence=dict(r.evidence or {}),
            fix_priority=r.fix_priority,
        )
        for r in issue_rows
    ]

    rec_rows = (
        db.execute(
            select(ScanRecommendation).where(ScanRecommendation.scan_id == scan.id).order_by(
                ScanRecommendation.priority.asc()
            )
        )
        .scalars()
        .all()
    )
    recommendations = [
        Recommendation(
            key=r.key,
            title=r.title,
            explanation=r.explanation,
            impact_scope=r.impact_scope,
            priority=r.priority,
            effort=r.effort,
            expected_gain=r.expected_gain,
        )
        for r in rec_rows
    ]

    limitations: list[Limitation] = []
    if scan.limitations:
        for x in scan.limitations:
            if isinstance(x, dict):
                limitations.append(Limitation.model_validate(x))

    strengths = list(scan.strengths) if scan.strengths else []

    meta: dict[str, Any] = {
        "normalized_url": scan.normalized_url,
        "submitted_url": scan.submitted_url,
        "final_url": scan.final_url,
        "created_at": scan.created_at.isoformat() if scan.created_at else None,
        "started_at": scan.started_at.isoformat() if scan.started_at else None,
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "extraction_version": scan.extraction_version,
        "scoring_version": scan.scoring_version,
        "ruleset_version": scan.ruleset_version,
        "llm_prompt_version": scan.llm_prompt_version,
    }
    if scan.parent_scan_id:
        meta["parent_scan_id"] = str(scan.parent_scan_id)
    if scan.project_id:
        meta["project_id"] = str(scan.project_id)

    return ScanDetailResponse(
        scan_id=scan.id,
        status=_parse_scan_status(scan.status),
        page_type_detected=_parse_page_type(scan.page_type_detected),
        page_type_final=_parse_page_type(scan.page_type_final),
        analysis_confidence=_parse_confidence(scan.analysis_confidence),
        global_score=global_score,
        seo_score=seo_score,
        geo_score=geo_score,
        scores=scores,
        strengths=strengths,
        issues=issues,
        recommendations=recommendations,
        limitations=limitations,
        summary=scan.summary,
        extraction=extraction_model,
        error_code=scan.error_code,
        error_message=scan.error_message,
        meta=meta,
    )


def public_report_to_response(db: Session, public_id: str) -> PublicReportResponse | None:
    pr = (
        db.execute(select(PublicReport).where(PublicReport.public_id == public_id, PublicReport.is_enabled.is_(True)))
        .scalars()
        .first()
    )
    if pr is None:
        return None
    scan = pr.scan
    detail = scan_to_detail_response(db, scan.id)
    if detail is None:
        return None
    return PublicReportResponse(
        public_id=pr.public_id,
        scan_id=scan.id,
        submitted_url=scan.submitted_url,
        page_type=detail.page_type_final or detail.page_type_detected,
        analysis_confidence=detail.analysis_confidence,
        global_score=detail.global_score,
        seo_score=detail.seo_score,
        geo_score=detail.geo_score,
        scores=detail.scores,
        top_issues=detail.issues[:5],
        top_fixes=detail.recommendations[:5],
        limitations=detail.limitations,
        summary=detail.summary,
        analyzed_at=scan.completed_at.isoformat() if scan.completed_at else None,
        meta={
            k: v
            for k, v in detail.meta.items()
            if k in ("scoring_version", "ruleset_version", "llm_prompt_version")
        },
    )
