"""In-memory mock implementation of ScanWorkflowPort — correctly shaped contracts, no Postgres."""

from __future__ import annotations

import secrets
from uuid import UUID, uuid4

from app.core.url_norm import normalize_submitted_url
from app.domain.enums import AnalysisConfidence, PageType, ScanStatus
from app.schemas.api_contracts import (
    PageTypeOverrideRequest,
    PublicReportCreatedResponse,
    PublicReportResponse,
    RescanResponse,
    ScanCreateRequest,
    ScanDetailResponse,
    ScanResponse,
)


class MockScanWorkflow:
    def __init__(self) -> None:
        self._by_id: dict[UUID, ScanDetailResponse] = {}
        self._public_to_scan: dict[str, UUID] = {}

    def create_scan(self, body: ScanCreateRequest) -> ScanResponse:
        scan_id = uuid4()
        raw = str(body.url)
        normalized_url, _, _ = normalize_submitted_url(raw)
        detail = ScanDetailResponse(
            scan_id=scan_id,
            status=ScanStatus.QUEUED,
            page_type_detected=None,
            page_type_final=body.page_type_override,
            analysis_confidence=AnalysisConfidence.UNKNOWN,
            global_score=None,
            seo_score=None,
            geo_score=None,
            scores=None,
            strengths=[],
            issues=[],
            recommendations=[],
            limitations=[],
            extraction=None,
            error_code=None,
            error_message=None,
            meta={
                "submitted_url": raw,
                "normalized_url": normalized_url,
                "scoring_version": None,
                "ruleset_version": None,
                "llm_prompt_version": None,
            },
        )
        self._by_id[scan_id] = detail
        return ScanResponse(
            scan_id=scan_id,
            status=ScanStatus.QUEUED,
            submitted_url=raw,
            normalized_url=normalized_url,
        )

    def get_scan(self, scan_id: UUID) -> ScanDetailResponse:
        return self._by_id[scan_id]

    def rescan_scan(self, scan_id: UUID) -> RescanResponse:
        parent = self._by_id[scan_id]
        new_id = uuid4()
        child = parent.model_copy(
            update={
                "scan_id": new_id,
                "status": ScanStatus.QUEUED,
                "global_score": None,
                "seo_score": None,
                "geo_score": None,
                "scores": None,
                "extraction": None,
                "issues": [],
                "recommendations": [],
                "strengths": [],
                "limitations": [],
                "analysis_confidence": AnalysisConfidence.UNKNOWN,
                "error_code": None,
                "error_message": None,
                "meta": {
                    **parent.meta,
                    "parent_scan_id": str(parent.scan_id),
                },
            }
        )
        self._by_id[new_id] = child
        return RescanResponse(scan_id=new_id, parent_scan_id=parent.scan_id, status=ScanStatus.QUEUED)

    def override_page_type(self, scan_id: UUID, body: PageTypeOverrideRequest) -> ScanDetailResponse:
        cur = self._by_id[scan_id]
        updated = cur.model_copy(update={"page_type_final": body.page_type})
        self._by_id[scan_id] = updated
        return updated

    def create_public_report(self, scan_id: UUID) -> PublicReportCreatedResponse:
        _ = self._by_id[scan_id]
        public_id = secrets.token_urlsafe(12)
        self._public_to_scan[public_id] = scan_id
        return PublicReportCreatedResponse(public_id=public_id, url_path=f"/report/{public_id}")

    def get_public_report(self, public_id: str) -> PublicReportResponse:
        scan_id = self._public_to_scan[public_id]
        d = self._by_id[scan_id]
        submitted = str(d.meta.get("submitted_url", ""))
        return PublicReportResponse(
            public_id=public_id,
            scan_id=d.scan_id,
            submitted_url=submitted,
            page_type=d.page_type_final or d.page_type_detected,
            analysis_confidence=d.analysis_confidence,
            global_score=d.global_score,
            seo_score=d.seo_score,
            geo_score=d.geo_score,
            scores=d.scores,
            top_issues=d.issues[:5],
            top_fixes=d.recommendations[:5],
            limitations=d.limitations,
            analyzed_at=d.meta.get("completed_at"),
            meta={
                k: v
                for k, v in d.meta.items()
                if k in ("scoring_version", "ruleset_version", "llm_prompt_version")
            },
        )


mock_scan_workflow = MockScanWorkflow()
