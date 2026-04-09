from typing import Any

from pydantic import BaseModel, Field


class Issue(BaseModel):
    code: str
    title: str
    description: str = ""
    severity: str = "medium"
    impact_scope: str = ""
    evidence: dict[str, Any] = Field(default_factory=dict)
    fix_priority: int = 0
