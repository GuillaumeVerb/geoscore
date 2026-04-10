from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.scan import Scan


class ScanScore(Base):
    __tablename__ = "scan_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    scoring_version: Mapped[str] = mapped_column(Text, nullable=False)
    ruleset_version: Mapped[str] = mapped_column(Text, nullable=False)
    global_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    seo_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    geo_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    seo_subscores: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    geo_subscores: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    penalties: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    bonuses: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    scan: Mapped[Scan] = relationship("Scan", back_populates="scores")
