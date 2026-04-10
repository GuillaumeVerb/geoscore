from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.scan import Scan


class ScanFetchResult(Base):
    __tablename__ = "scan_fetch_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    http_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fetch_method: Mapped[str] = mapped_column(Text, nullable=False)
    render_success: Mapped[bool] = mapped_column(Boolean, default=False)
    final_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    html_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    main_text_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    load_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_probably_spa: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_blocked: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_auth_wall: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    scan: Mapped[Scan] = relationship("Scan", back_populates="fetch_results")
