from __future__ import annotations

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    key: str | None = None
    title: str
    explanation: str = ""
    impact_scope: str = ""
    priority: int = 0
    effort: str = ""
    expected_gain: str = Field(default="", description="Qualitative expected impact")
