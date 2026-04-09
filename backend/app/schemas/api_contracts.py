from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from app.domain.enums import AnalysisConfidence, PageType, ScanStatus
from app.schemas.extraction import ExtractionSchema
from app.schemas.issue import Issue
from app.schemas.limitation import Limitation
from app.schemas.recommendation import Recommendation
from app.schemas.score import ScoreBlock


class ScanCreateRequest(BaseModel):
    url: HttpUrl | str
    project_id: uuid.UUID | None = None
    page_type_override: PageType | None = Field(
        default=None,
        description="Optional override persisted as page_type_final at creation.",
    )


class ScanResponse(BaseModel):
    """Returned by POST /api/scans — minimal acknowledgment."""

    scan_id: uuid.UUID
    status: ScanStatus
    submitted_url: str
    normalized_url: str


class ScanDetailResponse(BaseModel):
    """Returned by GET /api/scans/{scan_id} and PATCH page-type — api-design result essentials + extensions."""

    scan_id: uuid.UUID
    status: ScanStatus
    page_type_detected: PageType | None = None
    page_type_final: PageType | None = None
    analysis_confidence: AnalysisConfidence | None = None
    global_score: float | None = None
    seo_score: float | None = None
    geo_score: float | None = None
    scores: ScoreBlock | None = Field(
        default=None,
        description="Structured scores; mirrors flat global/seo/geo when analysis has completed",
    )
    strengths: list[str] = Field(default_factory=list)
    issues: list[Issue] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    limitations: list[Limitation] = Field(default_factory=list)
    extraction: ExtractionSchema | None = None
    error_code: str | None = None
    error_message: str | None = None
    meta: dict[str, Any] = Field(
        default_factory=dict,
        description="Timestamps, URLs, scoring_version, ruleset_version, llm_prompt_version, parent_scan_id, …",
    )


class RescanResponse(BaseModel):
    """Returned by POST /api/scans/{scan_id}/rescan."""

    scan_id: uuid.UUID
    parent_scan_id: uuid.UUID
    status: ScanStatus


class PageTypeOverrideRequest(BaseModel):
    page_type: PageType


class PublicReportCreatedResponse(BaseModel):
    """Returned by POST /api/scans/{scan_id}/public-report."""

    public_id: str
    url_path: str = Field(..., description="Frontend path, e.g. /report/{public_id}")


class PublicReportResponse(BaseModel):
    """Returned by GET /api/public-reports/{public_id} — shareable subset."""

    public_id: str
    scan_id: uuid.UUID
    submitted_url: str
    page_type: PageType | None = None
    analysis_confidence: AnalysisConfidence | None = None
    global_score: float | None = None
    seo_score: float | None = None
    geo_score: float | None = None
    scores: ScoreBlock | None = None
    top_issues: list[Issue] = Field(default_factory=list)
    top_fixes: list[Recommendation] = Field(default_factory=list)
    limitations: list[Limitation] = Field(default_factory=list)
    analyzed_at: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


# Deprecated names (scaffold evolution)
ScanCreate = ScanCreateRequest
ScanStatusResponse = ScanDetailResponse
PageTypeOverrideBody = PageTypeOverrideRequest
PublicReportCreateResponse = PublicReportCreatedResponse
PublicReportOut = PublicReportResponse
