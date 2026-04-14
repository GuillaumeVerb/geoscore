# Release readiness (V1.5 → V2-ready)

GeoScore is **functionally strong** as an MVP. This document separates what blocks a **public release** from what can follow. **Scoring stays frozen** (`scoring-v1-cal03` / `ruleset-v1-cal03`). No billing redesign in this pass.

---

## 1. Audit — typical gaps (historical context)

The rows below motivated **P0 / P1** work; they are **not** the live gap list for RC sign-off. **For RC:** use **§2**, **`verify-deployment.md`**, **`release-candidate-checklist.md`**, and **§4** (implemented now).

| Area | Status before this doc / PR | Risk |
|------|-----------------------------|------|
| **CI** | No automated gate on push/PR | Regressions slip in |
| **Readiness vs liveness** | Only `GET /health` (process up) | Orchestrators cannot distinguish “up but DB dead” |
| **DB migrations** | `create_all` on boot only | Schema drift, no rollback story in prod |
| **Release checklist** | `verify-deployment.md` (manual) | Human steps not grouped as “release” |
| **Auth / secrets** | JWT placeholder rejected in prod env | OK; still need secret rotation runbook |
| **Demo** | `/report/demo-example` + mock fallback | OK for fresh env |
| **Docs** | README + verify-deployment | “Why / how” for operators could be one place |
| **Product copy / method** | In-app “how scoring works” + score footnotes | See **`docs/00-product/product-strengthening-plan.md`** |

**As of current mainline:** CI, **`GET /ready`**, and **Alembic** are implemented (see **§4**). Remaining RC risk is mostly **operational** (env, deploy, manual smoke), not “missing CI.”

---

## 2. Priority matrix

### P0 — must-have before a serious public release

- **Automated CI** on default branch / PRs: backend tests + frontend lint + typecheck (no scoring changes).
- **Readiness probe**: `GET /ready` — DB reachable when `USE_MOCK_WORKFLOW=false`; explicit skip when mock (so k8s/Railway can wire probes).
- **Single “release” doc** (this file) + keep **`verify-deployment.md`** as the hands-on checklist after deploy.
- **Production env**: `JWT_SECRET_KEY`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, `ENVIRONMENT=production` (already enforced vs placeholder JWT).

### P1 — strongly recommended before / shortly after release

- **Alembic**: versioned migrations in-repo (`backend/alembic/`); app startup runs `upgrade head` when `USE_MOCK_WORKFLOW=false` — see **`database-migrations.md`**. For DBs that only ever used `create_all`, use **`alembic stamp`** once (documented there).
- **Integration smoke in CI** (optional job): Postgres service + `verify_scan_api.py` on PRs to main (slower, catches wiring).
- **Structured logging + request id** (minimal): easier incident triage.
- **Rate limits / abuse** on `POST /api/auth/session` and `POST /api/scans` (light, e.g. slowapi or proxy-level).
- **Security headers** on Next.js / reverse proxy (CSP baseline, HSTS on prod domain).
- **api-design.md** kept in sync with auth + `/ready` for integrators.

### P2 — after release (explicitly defer)

- Billing / Stripe, usage tiers, admin multi-tenant.
- Magic-link email, password accounts, SSO.
- Full observability stack (APM, dashboards).
- Multi-region, read replicas, advanced cache layers.
- Broad refactors or new product surfaces not in vision.md.

---

## 3. Recommended implementation order (engineering)

1. **CI** — highest leverage, smallest scope; protects everything below.  
2. **`/ready`** — unlocks correct deploy health checks.  
3. **This doc + verify-deployment cross-links** — operators know P0 vs P1.  
4. **Alembic bootstrap** (P1) — first migration = current schema snapshot; then every DDL change ships as a revision.  
5. **CI integration job** (P1) — once migrations exist for a disposable DB.  
6. **Rate limits / logging** (P1) — as traffic or compliance requires.

---

## 4. What this repository implements now (P0 subset)

- GitHub Actions **CI** (`backend` pytest, `frontend` lint + typecheck).
- **`GET /ready`** on the FastAPI app (see `README.md`).
- This **release-readiness** plan + pointers in **README** / **verify-deployment**.

Remaining P0 is mostly **operational**: set secrets, run checklist, monitor first deploy.

---

## 5. Release candidate (final polish)

Before tagging an RC: **`docs/03-build/release-candidate-checklist.md`** — bug bash on critical flows + manual pass on **5–10 real URLs**; only fix **truly blocking** issues (no feature or scoring expansion).

## 6. Release day (minimal)

1. Merge with **CI green**.  
2. Apply env per **README** (prod JWT, CORS, DB URL, frontend API URL).  
3. Deploy API → confirm **`/health`** and **`/ready`** (200 when DB up).  
4. Deploy frontend → run **`docs/03-build/verify-deployment.md`**.  
5. Smoke **demo** `/report/demo-example` in a clean browser profile.

---

## 7. Explicit “wait until after release”

- Billing, email verification, enterprise auth, heavy infra, scoring recalibration, new scoring surfaces.
