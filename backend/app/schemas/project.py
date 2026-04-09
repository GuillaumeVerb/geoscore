from __future__ import annotations

import uuid

from pydantic import BaseModel


class ProjectRead(BaseModel):
    """API shape for a project row (routes will use this in later sprints)."""

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
