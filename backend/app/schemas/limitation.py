from pydantic import BaseModel, Field


class Limitation(BaseModel):
    """User-facing analysis limitation (aligned with pipeline partial/limited states)."""

    code: str = Field(..., description="Stable machine code")
    message: str = Field(..., description="Human-readable explanation")
    severity: str = Field(default="info", description="info | warning | error")
