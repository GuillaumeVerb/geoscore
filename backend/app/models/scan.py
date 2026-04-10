from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional  # noqa: TC003 — Any used in JSONB strengths

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.public_report import PublicReport
    from app.models.scan_extraction import ScanExtraction
    from app.models.scan_fetch_result import ScanFetchResult
    from app.models.scan_issue import ScanIssue
    from app.models.scan_recommendation import ScanRecommendation
    from app.models.scan_score import ScanScore
    from app.models.user import User


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    parent_scan_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=True)

    submitted_url: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_url: Mapped[str] = mapped_column(Text, nullable=False)
    final_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(Text, nullable=False, default="created")
    analysis_mode: Mapped[str] = mapped_column(Text, nullable=False, default="standard")
    scan_trigger: Mapped[str] = mapped_column(Text, nullable=False, default="manual")

    page_type_detected: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_type_final: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_type_confidence: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), nullable=True)
    analysis_confidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    extraction_version: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scoring_version: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ruleset_version: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    llm_prompt_version: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    limitations: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strengths: Mapped[Optional[list[Any]]] = mapped_column(JSONB, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[Optional[User]] = relationship("User", back_populates="scans")
    project: Mapped[Optional[Project]] = relationship("Project", back_populates="scans")
    parent_scan: Mapped[Optional[Scan]] = relationship("Scan", remote_side=[id], foreign_keys=[parent_scan_id])
    public_reports: Mapped[list[PublicReport]] = relationship("PublicReport", back_populates="scan")
    fetch_results: Mapped[list[ScanFetchResult]] = relationship(
        "ScanFetchResult", back_populates="scan", cascade="all, delete-orphan"
    )
    extractions: Mapped[list[ScanExtraction]] = relationship(
        "ScanExtraction", back_populates="scan", cascade="all, delete-orphan"
    )
    scores: Mapped[list[ScanScore]] = relationship(
        "ScanScore", back_populates="scan", cascade="all, delete-orphan"
    )
    issues: Mapped[list[ScanIssue]] = relationship(
        "ScanIssue", back_populates="scan", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list[ScanRecommendation]] = relationship(
        "ScanRecommendation", back_populates="scan", cascade="all, delete-orphan"
    )
