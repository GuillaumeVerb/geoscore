"""Postgres public reports — optional; routes use MockScanWorkflow until swapped in deps."""

from __future__ import annotations

import secrets

from sqlalchemy.orm import Session

from app.domain.enums import AnalysisConfidence, PageType
from app.models.public_report import PublicReport
from app.models.scan import Scan
from app.schemas.api_contracts import PublicReportResponse


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


class ReportService:
    def create_or_enable_public_report(self, db: Session, scan: Scan) -> PublicReport:
        existing = db.query(PublicReport).filter(PublicReport.scan_id == scan.id).first()
        if existing:
            existing.is_enabled = True
            db.commit()
            db.refresh(existing)
            return existing

        public_id = secrets.token_urlsafe(12)
        row = PublicReport(scan_id=scan.id, public_id=public_id, is_enabled=True)
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    def get_by_public_id(self, db: Session, public_id: str) -> PublicReport | None:
        return (
            db.query(PublicReport)
            .filter(PublicReport.public_id == public_id, PublicReport.is_enabled.is_(True))
            .first()
        )

    def to_public_response(self, scan: Scan, public_id: str) -> PublicReportResponse:
        """Reduced shareable view; issues/fixes populated when scan artifacts exist."""
        return PublicReportResponse(
            public_id=public_id,
            scan_id=scan.id,
            submitted_url=scan.submitted_url,
            page_type=_parse_page_type(scan.page_type_final or scan.page_type_detected),
            analysis_confidence=_parse_confidence(scan.analysis_confidence),
            global_score=None,
            seo_score=None,
            geo_score=None,
            scores=None,
            top_issues=[],
            top_fixes=[],
            limitations=[],
            analyzed_at=scan.completed_at.isoformat() if scan.completed_at else None,
            meta={"ruleset_version": scan.ruleset_version, "scoring_version": scan.scoring_version},
        )


report_service = ReportService()
