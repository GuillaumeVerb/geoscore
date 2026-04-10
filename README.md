# GeoScore

GeoScore is a minimal SEO & GEO analyzer for websites and apps. This repository contains product docs, a **Next.js** frontend, a **FastAPI** backend, and **Postgres** (via Docker for local dev).

## Layout

```
geoscore/
├── backend/           # FastAPI app (`app/` package)
├── frontend/          # Next.js App Router
├── docs/              # Product & architecture specs
├── docker-compose.yml # Local Postgres only
├── AGENTS.md
└── README.md
```

## Prerequisites

- **Python 3.10+** recommended (3.9 works with `eval-type-backport` in `backend/requirements.txt`).
- **Node.js 20+** for the frontend.
- **Docker** (optional) for Postgres: `docker compose up -d`.

## Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Ensure DATABASE_URL points at Postgres, then:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET http://localhost:8000/health`
- API: `POST /api/scans`, `GET /api/scans/{scan_id}`, etc. (see `docs/01-architecture/api-design.md`)

Tables are created on startup (`Base.metadata.create_all`) for local scaffolding — migrate to Alembic before production.

Scan API routes use an in-memory **`MockScanWorkflow`** by default (`get_scan_workflow` in `app/api/deps.py`). Swap this dependency for a Postgres-backed class implementing `ScanWorkflowPort` when wiring persistence.

## Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` to the API origin (default `http://localhost:8000`). The browser calls this URL directly, so it must match where FastAPI listens (including port).

### CORS (local dev)

The Next.js app (e.g. `http://localhost:3000`) and the API (e.g. `http://localhost:8000`) are different origins. FastAPI must allow the frontend origin via `CORSMiddleware` (`CORS_ORIGINS` in `backend/.env`, see `backend/.env.example`). If you change the Next port, add it to `CORS_ORIGINS` as a comma-separated list.

## Stack (from docs)

- Frontend: Next.js  
- Backend: FastAPI  
- Database: Postgres  
- Rendering: Playwright (service placeholder in `backend/app/services/render_service.py`)  
- LLM: interface only (`llm_service`) — not implemented in scaffold  

## Further reading

1. `AGENTS.md`  
2. `docs/01-architecture/architecture-overview.md`  
3. `docs/03-build/implementation-roadmap.md`  
