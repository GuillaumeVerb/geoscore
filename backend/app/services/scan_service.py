"""Postgres scan persistence — optional; routes use MockScanWorkflow until swapped in deps."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.url_norm import normalize_submitted_url
from app.domain.enums import AnalysisConfidence, PageType, ScanStatus
from app.models.scan import Scan
from app.schemas.api_contracts import ScanCreateRequest, ScanDetailResponse
from app.schemas.limitation import Limitation
from app.services.extraction_service import extraction_service
from app.services.scoring_service import scoring_service


def _parse_scan_status(value: str) -> ScanStatus:
    try:
        return ScanStatus(value)
    except ValueError:
        return ScanStatus.QUEUED


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


class ScanService:
    def create_scan(self, db: Session, body: ScanCreateRequest) -> Scan:
        raw = str(body.url)
        normalized, domain, path = normalize_submitted_url(raw)
        scan = Scan(
            submitted_url=raw,
            normalized_url=normalized,
            domain=domain,
            path=path,
            status=ScanStatus.QUEUED.value,
            project_id=body.project_id,
            page_type_final=body.page_type_override.value if body.page_type_override else None,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        return scan

    def get_scan(self, db: Session, scan_id: UUID) -> Scan | None:
        return db.query(Scan).filter(Scan.id == scan_id).first()

    def to_detail_response(self, scan: Scan) -> ScanDetailResponse:
        extraction = None
        scores = None
        strengths: list[str] = []
        issues = []
        recommendations = []
        limitations: list[Limitation] = []

        if scan.limitations:
            limitations = [Limitation.model_validate(x) for x in scan.limitations if isinstance(x, dict)]

        if scan.status == ScanStatus.COMPLETED.value:
            scores, issues, recommendations = scoring_service.score_placeholder()
            extraction = extraction_service.build_placeholder(str(scan.id))

        return ScanDetailResponse(
            scan_id=scan.id,
            status=_parse_scan_status(scan.status),
            page_type_detected=_parse_page_type(scan.page_type_detected),
            page_type_final=_parse_page_type(scan.page_type_final),
            analysis_confidence=_parse_confidence(scan.analysis_confidence),
            global_score=scores.global_score if scores else None,
            seo_score=scores.seo_score if scores else None,
            geo_score=scores.geo_score if scores else None,
            scores=scores,
            strengths=strengths,
            issues=issues,
            recommendations=recommendations,
            limitations=limitations,
            summary=None,
            extraction=extraction,
            error_code=scan.error_code,
            error_message=scan.error_message,
            meta={
                "normalized_url": scan.normalized_url,
                "submitted_url": scan.submitted_url,
                "created_at": scan.created_at.isoformat() if scan.created_at else None,
                "extraction_version": scan.extraction_version,
                "scoring_version": scan.scoring_version,
                "ruleset_version": scan.ruleset_version,
                "llm_prompt_version": scan.llm_prompt_version,
            },
        )

    def rescan(self, db: Session, parent: Scan) -> Scan:
        child = Scan(
            user_id=parent.user_id,
            project_id=parent.project_id,
            parent_scan_id=parent.id,
            submitted_url=parent.submitted_url,
            normalized_url=parent.normalized_url,
            final_url=parent.final_url,
            domain=parent.domain,
            path=parent.path,
            status=ScanStatus.QUEUED.value,
            analysis_mode=parent.analysis_mode,
            scan_trigger="rescan",
            page_type_final=parent.page_type_final,
        )
        db.add(child)
        db.commit()
        db.refresh(child)
        return child

    def apply_page_type_override(self, db: Session, scan: Scan, page_type: PageType) -> Scan:
        scan.page_type_final = page_type.value
        db.commit()
        db.refresh(scan)
        return scan


scan_service = ScanService()
