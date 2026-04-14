from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, HttpUrl

from app.domain.enums import AnalysisConfidence, PageType, ScanStatus
from app.schemas.extraction import ExtractionSchema
from app.schemas.issue import Issue
from app.schemas.limitation import Limitation
from app.schemas.recommendation import Recommendation
from app.schemas.score import ScoreBlock


class SessionCreateRequest(BaseModel):
    """MVP sign-in: email only (no magic-link delivery in this milestone)."""

    email: EmailStr


class UserSummary(BaseModel):
    id: uuid.UUID
    email: str


class SessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary


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


class ScanSummaryItem(BaseModel):
    """Light row for GET /api/scans — dashboard / history."""

    scan_id: uuid.UUID
    status: ScanStatus
    submitted_url: str
    domain: str
    page_type_detected: PageType | None = None
    page_type_final: PageType | None = None
    analysis_confidence: AnalysisConfidence | None = None
    global_score: float | None = None
    seo_score: float | None = None
    geo_score: float | None = None
    created_at: datetime
    completed_at: datetime | None = None
    project_id: uuid.UUID | None = None
    parent_scan_id: uuid.UUID | None = None


class ScansListResponse(BaseModel):
    """Returned by GET /api/scans."""

    scans: list[ScanSummaryItem] = Field(default_factory=list)


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
    summary: str | None = Field(
        default=None,
        description="Short narrative for the report UI; optional until LLM/summary pipeline exists",
    )
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


class ScanCompareScores(BaseModel):
    global_score: float | None = None
    seo_score: float | None = None
    geo_score: float | None = None


class ScanCompareResponse(BaseModel):
    """Before/after presentation for a rescan pair (parent = before, child = after)."""

    parent_scan_id: uuid.UUID
    child_scan_id: uuid.UUID
    submitted_url: str
    before_scores: ScanCompareScores
    after_scores: ScanCompareScores
    resolved_issues: list[Issue] = Field(default_factory=list)
    new_issues: list[Issue] = Field(default_factory=list)
    recommendations_persistent: list[Recommendation] = Field(default_factory=list)
    recommendations_new: list[Recommendation] = Field(default_factory=list)
    recommendations_removed: list[Recommendation] = Field(default_factory=list)


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
    summary: str | None = None
    analyzed_at: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


# Deprecated names (scaffold evolution)
ScanCreate = ScanCreateRequest
ScanStatusResponse = ScanDetailResponse
PageTypeOverrideBody = PageTypeOverrideRequest
PublicReportCreateResponse = PublicReportCreatedResponse
PublicReportOut = PublicReportResponse
