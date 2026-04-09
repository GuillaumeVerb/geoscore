from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ScoreBlock(BaseModel):
    """Structured scores: global / SEO / GEO plus sub-scores (database-schema scan_scores shape)."""

    global_score: float | None = None
    seo_score: float | None = None
    geo_score: float | None = None
    seo_subscores: dict[str, Any] = Field(default_factory=dict)
    geo_subscores: dict[str, Any] = Field(default_factory=dict)
    penalties: dict[str, Any] = Field(default_factory=dict)
    bonuses: dict[str, Any] = Field(default_factory=dict)
    confidence_score: float | None = Field(
        default=None, description="Numeric companion to analysis_confidence label when available"
    )


# Back-compat for any code still importing ScoreResult
ScoreResult = ScoreBlock
