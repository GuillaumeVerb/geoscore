"""Pytest bootstrapping — keep FastAPI lifespan from requiring Postgres in unit tests."""

from __future__ import annotations

import os

# Force mock workflow for the pytest process so ``app`` lifespan never runs Alembic
# (avoids requiring Postgres for the default unit suite). Override in a dedicated integration job if needed.
os.environ["USE_MOCK_WORKFLOW"] = "true"
