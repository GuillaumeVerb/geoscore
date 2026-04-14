import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routes import auth, projects, public_reports, scans
from app.core.config import settings
from app.db.migrate import run_alembic_upgrade_to_head
from app.db.session import engine

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Schema: Alembic migrations are the source of truth (see docs/03-build/database-migrations.md).
    # Mock workflow has no persistent Postgres schema to migrate.
    if not settings.use_mock_workflow and settings.run_alembic_on_startup:
        log.info("Running Alembic upgrade head (set RUN_ALEMBIC_ON_STARTUP=false if migrations run in pre-deploy).")
        run_alembic_upgrade_to_head()
        log.info("Alembic upgrade head finished.")
    elif not settings.use_mock_workflow:
        log.warning(
            "RUN_ALEMBIC_ON_STARTUP=false: skipping Alembic at startup; ensure migrations ran (e.g. Railway pre-deploy)."
        )
    yield


app = FastAPI(title="GeoScore API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(scans.router, prefix="/api")
app.include_router(public_reports.router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness: process is up (use for cheap probes)."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    """Readiness: DB reachable when using Postgres workflow; mock mode skips DB."""
    if settings.use_mock_workflow:
        return {"status": "ready", "database": "skipped", "workflow": "mock"}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from None
    return {"status": "ready", "database": "ok", "workflow": "postgres"}
