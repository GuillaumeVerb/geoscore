# Verify setup / deployment

Quick manual checks after **backend + frontend + Postgres** (if using real workflow) are configured. Scoring is unchanged; this validates wiring and auth.

## Preconditions

- Backend `.env`: `DATABASE_URL` if `USE_MOCK_WORKFLOW=false`; `CORS_ORIGINS` includes the frontend origin; `JWT_SECRET_KEY` set in production.
- First time on Postgres: either start the API once (runs **`alembic upgrade head`**) or run it manually from `backend/` — see **`docs/03-build/database-migrations.md`**. If the DB was created only with legacy `create_all`, **`alembic stamp 20250409120000`** once before relying on upgrades.
- Frontend `.env.local`: `NEXT_PUBLIC_API_URL` points at the API origin (browser calls it directly).
- Optional: `playwright install chromium` if `PLAYWRIGHT_ENABLED=true`.

### Split deploy (frontend + API on different hosts)

Typical last-mile breaks — check **before** blaming scoring or “random” scan failures:

- **`NEXT_PUBLIC_API_URL`** (frontend build-time env): must be the **public** API base URL the **browser** can reach (same scheme you expect users to use: **HTTPS** in production). **No trailing slash** (the app strips one if present, but set it clean). Wrong URL → all authenticated calls fail or appear as CORS errors in DevTools.
- **`CORS_ORIGINS`** (backend): comma-separated list of **exact** frontend origins (`https://app.example.com`, `http://localhost:3000`). Must include **every** origin users hit (preview URL, custom domain). FastAPI uses **credentials**; a missing or wrong origin → browser blocks `fetch` before the API runs your handler.
- **HTTPS:** a page served over **https** cannot call an **http** API (mixed content). API must be HTTPS in production if the app is HTTPS.
- **`PLAYWRIGHT_ENABLED`:** if the API host cannot run Chromium, set **`PLAYWRIGHT_ENABLED=false`** and accept HTTP-only capture for some pages — otherwise scans may fail at render with opaque pipeline errors.

## Checklist

1. **Backend liveness** — `GET {API}/health` → `{"status":"ok"}`.
1b. **Backend readiness** — `GET {API}/ready` → **200** with `database: ok` when using Postgres (`USE_MOCK_WORKFLOW=false`); **200** with `database: skipped` when mock workflow; **503** if Postgres is required but unreachable.
2. **Landing** — Open `/`; marketing and URL form load.
3. **Demo report (no auth)** — Open `/report/demo-example`; content loads (API mock fallback is OK if API is down).
4. **Sign in** — `/sign-in`, submit email; redirected; nav shows account affordance.
5. **Create scan** — From `/`, submit a real URL (requires session); lands on `/scan/{id}` and result progresses or completes.
6. **Dashboard** — `/dashboard` lists only your scans; empty state if none.
7. **Scan detail** — Open a scan you own; 404-style unavailable if UUID is wrong or another user’s scan.
8. **Public report** — From a completed scan, create/share public link; open `/report/{public_id}` in a **private window** (no token); report loads.

## Short V2 smoke test

Focused check for **Projects** + **Compare to previous run** only (no new features; aligns with `docs/03-build/short-v2-execution-plan.md`). Use a normal signed-in session; **Postgres** (`USE_MOCK_WORKFLOW=false`) recommended so rescans and lineage persist like production.

1. Sign in.
2. Create project.
3. Filter dashboard by project.
4. Create a new scan in that project.
5. Rescan from a result.
6. Open compare from result page.
7. Open compare from dashboard.
8. Verify safe 404 behavior for a scan without parent comparison (e.g. open `/scan/{id}/compare` for a scan that has no rescan parent — expect a controlled error, not a blank or crashed UI).

## Scripts

**RC sign-off (manual):** after deploy (or prod-like env), run **`release-candidate-checklist.md`** (bug bash §2 + §3 URL pass) once **Full manual smoke** below has passed.

- Backend unit tests (from `backend/`): `python -m pytest -q`
- Frontend typecheck: `npm run typecheck` (in `frontend/`)
- Optional API smoke (from `backend/`, API running):  
  `python scripts/verify_scan_api.py --base http://127.0.0.1:8000 --email you@example.com --url https://example.com`

## Mock vs real

| Mode | When | Scans / DB |
|------|------|------------|
| `USE_MOCK_WORKFLOW=true` | No Postgres, UI demo | In-memory only |
| `USE_MOCK_WORKFLOW=false` | Normal local / prod | Postgres + pipeline |

Auth (`POST /api/auth/session`, Bearer on scan routes) applies in **both** modes.

---

## Full manual smoke (ordered)

Run once after **deploy** (or local prod-like env). Replace `{API}` with your public API origin (no trailing slash). Use **Postgres** (`USE_MOCK_WORKFLOW=false`) for steps that need persistence (rescans, projects).

1. `GET {API}/health` → `{"status":"ok"}`.
2. `GET {API}/ready` → **200** and `database: ok` when Postgres is required; **503** means do not ship — DB or config is wrong.
3. Open deployed **frontend** `/` — landing loads; no console errors blocking the form.
4. `/report/demo-example` in a **private** window — demo content loads (mock fallback OK if API unreachable for this route only).
5. `/sign-in` — sign in; confirm session (nav / return path).
6. From `/`, submit a real URL — lands on `/scan/{id}`; wait for a **final** status (completed / partial / failed) as appropriate.
7. `/dashboard` — only your scans; empty state if none.
8. Open a scan you own; wrong UUID or another user’s scan → safe error (no data leak).
9. From a **completed** scan (if you have one): create **public report**; open `/report/{public_id}` in a **private** window — loads without Bearer.
10. **Short V2 smoke test** (section above) — projects, filter, scan in project, rescan, compare from result + dashboard, 404 on compare without parent.

Then (optional but recommended): `python -m pytest -q` (backend) and `npm run lint && npm run typecheck` (frontend) on the **same commit** you deployed, or rely on CI green on that commit.
