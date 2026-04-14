from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ProjectRead(BaseModel):
    """API shape for a project row."""

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    created_at: datetime


class ProjectsListResponse(BaseModel):
    projects: list[ProjectRead] = Field(default_factory=list)
