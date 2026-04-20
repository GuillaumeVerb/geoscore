# GeoScore

Minimal SEO & GEO analyzer: one URL in, one structured result. This repo has a **Next.js** frontend, **FastAPI** backend, **Postgres**, and product docs under `docs/`.

**Scoring is frozen** at `scoring-v1-cal03` / `ruleset-v1-cal03` — do not change calibration in passing tasks.

## Repository layout

```
geoscore/
├── backend/           # FastAPI (`app/` package)
├── frontend/          # Next.js App Router
├── docs/              # Specs and runbooks
├── docker-compose.yml # Local Postgres only
├── AGENTS.md
└── README.md
```

## Prerequisites

| Tool | Notes |
|------|--------|
| **Python 3.10+** | 3.9 works with `eval-type-backport` in `backend/requirements.txt`. |
| **Node.js 20+** | For the frontend. |
| **Docker** | Optional: `docker compose up -d` for Postgres on `localhost:5432`. |
| **Playwright browsers** | Optional but recommended if `PLAYWRIGHT_ENABLED=true` (default): after `pip install -r requirements.txt`, run `playwright install chromium`. |

## Environment files

| App | Template | Local file |
|-----|------------|------------|
| Backend | `backend/.env.example` | `backend/.env` |
| Frontend | `frontend/.env.example` | `frontend/.env.local` |

Next.js only loads `frontend/.env.local` (or `.env`); the root `.env.example` is an index only.

### Backend variables (summary)

- **`DATABASE_URL`** — Required when **`USE_MOCK_WORKFLOW=false`** (default). Matches `docker-compose.yml` credentials unless you override.
- **`USE_MOCK_WORKFLOW`** — `true` = in-memory scans, no Postgres. `false` = real **Postgres** pipeline.
- **`CORS_ORIGINS`** — Comma-separated allowed browser origins (e.g. `http://localhost:3000`). **Production:** include your deployed frontend URL(s).
- **`ENVIRONMENT`** — `development` (default) or `production`. In **production**, the app **refuses to start** if `JWT_SECRET_KEY` is still the dev placeholder.
- **`JWT_SECRET_KEY`**, **`JWT_EXPIRE_DAYS`** — MVP session signing; set a strong secret in production (`openssl rand -hex 32`).
- **`PLAYWRIGHT_ENABLED`** — Set `false` on hosts without Chromium if you accept HTTP-only capture for edge pages.

### Frontend variables

- **`NEXT_PUBLIC_API_URL`** — Full API origin, **no trailing slash** (default `http://localhost:8000`). The browser calls the API from the user’s machine, so this must be reachable from the client (local dev or public HTTPS).

## Run the backend

```bash
cd backend
cp .env.example .env
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium   # optional; skip if PLAYWRIGHT_ENABLED=false
```

With Postgres (recommended for real scans):

```bash
# from repo root
docker compose up -d
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Liveness:** `GET http://localhost:8000/health` — process is up.
- **Readiness:** `GET http://localhost:8000/ready` — when `USE_MOCK_WORKFLOW=false`, checks Postgres (`SELECT 1`); returns **503** if the DB is unreachable. When `USE_MOCK_WORKFLOW=true`, returns **200** with `database: skipped` (no DB required).
- API routes: `/api/...` (see `docs/01-architecture/api-design.md`)

**Schema / migrations:** Alembic is configured under `backend/alembic/`. With **`USE_MOCK_WORKFLOW=false`**, the API runs **`alembic upgrade head`** on startup (see `app/main.py` and **`docs/03-build/database-migrations.md`**). New DB: start the app or run `python -m alembic upgrade head` from `backend/`. Existing DB built only with old `create_all`: **stamp once** (`alembic stamp 20250409120000`) then use upgrades — details in that doc.

## Run the frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. Ensure **`CORS_ORIGINS`** on the backend includes `http://localhost:3000` (or whatever port Next uses).

## Auth (MVP)

Scan APIs require **`Authorization: Bearer <jwt>`**. The UI stores the token in **`sessionStorage`** after **`POST /api/auth/session`** (email only, no magic link yet).

- **Sign in** before analyzing a URL from the landing form (redirects to `/sign-in` if needed).
- **`GET /api/public-reports/{public_id}`** stays **public** (no Bearer).

## Mock vs real workflow

| `USE_MOCK_WORKFLOW` | Postgres | Behavior |
|---------------------|----------|----------|
| `false` (default) | Required | Persistent scans, real pipeline, Playwright optional path. |
| `true` | Not used | In-memory scans for UI / demos without DB. |

Auth applies in both modes.

## Tests and typecheck

**Backend** (from `backend/`; `pytest.ini` sets `pythonpath = .`):

```bash
python -m pytest -q
```

**Frontend**:

```bash
cd frontend && npm run lint && npm run typecheck
```

## Optional API smoke script

With the API running and **Postgres + real workflow** (or mock, if scan routes still work end-to-end):

```bash
cd backend
python scripts/verify_scan_api.py --base http://127.0.0.1:8000 --email dev@example.com --url https://example.com
```

## Deploy notes (minimal)

### Railway (API — monorepo)

Railway’s builder only sees **the service root directory**. If the root is the **repo root**, there is no `requirements.txt` there → Railpack won’t detect Python (errors like “start.sh not found” / wrong language).

1. In the **API** service: **Settings → Root directory** = `backend` (folder that contains `requirements.txt` and `app/`).
2. **Config as code:** Railway merges `backend/railway.json` — set the service’s config file path to **`backend/railway.json`** if it is not picked up automatically (Railway’s config file path is from the **repository root**, not from the root directory).
3. Env vars: same as “Deploy notes” below (`ENVIRONMENT`, `JWT_SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`, etc.).
4. **`connection refused` to `localhost:5432`** or stuck on startup: the API is still using the **dev default** `DATABASE_URL` (localhost). On Railway, open the **API** service → **Variables** → add **`DATABASE_URL`** using **Reference** to your **Postgres** service’s `DATABASE_URL` (not a hand-typed localhost URL). Linked variables are reliably available when the **container starts**; migrations run then (`RUN_ALEMBIC_ON_STARTUP`, default `true`). In production, a localhost DB URL now **fails fast** with an explicit config error.

---

1. Set **`ENVIRONMENT=production`**, **`JWT_SECRET_KEY`** (strong random), **`DATABASE_URL`**, **`USE_MOCK_WORKFLOW=false`** on the API host.
2. Set **`CORS_ORIGINS`** to every frontend origin that will call the API (comma-separated, **exact** scheme + host + port). Include preview URLs if you use them. Missing origin → browser CORS errors (often mistaken for “API down”).
3. On the frontend host (e.g. Vercel), set **`NEXT_PUBLIC_API_URL`** at **build** time to the **public** API base URL (**HTTPS** if the site is HTTPS). **No trailing slash.** The browser calls the API from the user’s machine — this must be reachable and must not be mixed-content (**https** page → **https** API).
4. If the API host cannot run Playwright/Chromium, set **`PLAYWRIGHT_ENABLED=false`** on the backend (see `backend/.env.example`).
5. **After deploy:** run the ordered checklist in **`docs/03-build/verify-deployment.md`** (section **Full manual smoke**), including **Short V2 smoke test** if you ship Projects + compare.

## Demo / example report

- **`/report/demo-example`** uses the static id `demo-example`. If the API has no row, the UI falls back to **mock** data so the page still works in a fresh clone.

## Further reading

- `AGENTS.md` — product and scoring rules for agents.
- `docs/00-product/product-strengthening-plan.md` — pre-release product quality (method, credibility, UX priorities).
- `docs/00-product/roadmap-v2-v3.md` — disciplined V2 / V3 product roadmap (post–V1.5).
- `docs/00-product/blog-strategy.md` — product-led blog framing; first post lives at **`/blog`** in the Next app.
- `docs/01-architecture/architecture-overview.md`
- `docs/03-build/release-readiness.md` — **P0 / P1 / P2** release plan and what ships vs deferred
- `docs/03-build/verify-deployment.md` — post-setup checklist
- `docs/03-build/release-candidate-checklist.md` — RC bug bash + 5–10 real URLs (no extra scope)
- `docs/03-build/implementation-roadmap.md`

**CI:** `.github/workflows/ci.yml` runs backend pytest and frontend lint + typecheck on push/PR to `main` or `master`.
