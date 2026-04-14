# Database migrations (Alembic)

GeoScore uses **Alembic** in `backend/alembic/` with revisions under `alembic/versions/`. SQLAlchemy models in `app/models/` remain the **declarative** source of truth; each schema change should ship a **new revision** that matches the ORM.

## Current layout

| Path | Role |
|------|------|
| `backend/alembic.ini` | Alembic entry config (`script_location = alembic`) |
| `backend/alembic/env.py` | Loads `Base.metadata`, `DATABASE_URL` / settings |
| `backend/alembic/versions/` | Revision scripts |
| `backend/app/db/migrate.py` | `run_alembic_upgrade_to_head()` for app startup |

## Baseline revision

- **`20250409120000_baseline`** — creates all tables for the current V1 ORM (Postgres).

## Initialize a **new** database

From `backend/` with Postgres running and `DATABASE_URL` set (or `.env`):

```bash
cd backend
python -m alembic upgrade head
```

Or start the API with **`USE_MOCK_WORKFLOW=false`**: on startup the app runs **`alembic upgrade head`** automatically (same as above), unless **`RUN_ALEMBIC_ON_STARTUP=false`** (e.g. you run migrations in your own release job). Postgres connections use a **15s connect timeout** so a bad `DATABASE_URL` fails fast instead of blocking startup indefinitely.

**Railway:** reference **`DATABASE_URL`** from the Postgres service on the **API** service. Do not rely on a localhost URL in production; the app validates that in **`ENVIRONMENT=production`** when using the real workflow.

## Existing database (was created with `create_all` only)

If tables **already exist** and match this baseline but there is **no** `alembic_version` row, do **not** run `upgrade` (it would try to `CREATE TABLE` again). Stamp once:

```bash
cd backend
python -m alembic stamp 20250409120000
```

After that, use **`upgrade head`** for all future revisions.

## Create a new revision (after ORM / schema change)

1. Edit models in `app/models/`.
2. Autogenerate (requires DB that reflects **current** migration state — usually dev DB at head):

```bash
cd backend
python -m alembic revision --autogenerate -m "describe_change"
```

3. **Review** the generated file (autogenerate is not perfect).
4. Apply locally:

```bash
python -m alembic upgrade head
```

5. Commit the new file under `alembic/versions/`.

Hand-written revisions are fine when autogenerate is noisy.

## Deploy

Run migrations **before** or as part of process start:

```bash
cd backend && python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The FastAPI lifespan also runs **`upgrade head`** when **`USE_MOCK_WORKFLOW=false`**, so a single-instance deploy self-heals schema on boot. For **multi-instance** production, prefer running migrations **once** in a release job, then roll app replicas (avoids concurrent migration races).

## Tests

- **`tests/conftest.py`** sets **`USE_MOCK_WORKFLOW=true`** so pytest does not require Postgres for the default suite.
- **`tests/test_alembic_graph.py`** checks `alembic heads` (no DB).

## Rules of thumb

- Do not edit applied revisions; add a new one.
- Ship migrations in the **same PR** as ORM changes that require DDL.
- Test `upgrade` on a copy of production-like data before release.

See **`release-readiness.md`** for release ordering.
