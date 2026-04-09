from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.scan import Scan


class User(Base):
    """Placeholder user row for future auth; scans may reference user_id."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[Optional[str]] = mapped_column(Text, unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    plan_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    projects: Mapped[list[Project]] = relationship("Project", back_populates="user")
    scans: Mapped[list[Scan]] = relationship("Scan", back_populates="user")
