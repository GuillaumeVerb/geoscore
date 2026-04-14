# GeoScore — short V2 frame (Projects + Compare to previous run)

**Status:** product / implementation framing (not a feature brainstorm).  
**Baseline:** V1.5 stable. **Scoring frozen:** `scoring-v1-cal03` / `ruleset-v1-cal03` — no calibration or engine reopen for this slice.  
**Scope lock:** This document defines **short V2 only**. Broader items in `vision.md` (multi-page, site-level, competitor, etc.) are **not** part of short V2; sequencing follows `roadmap-v2-v3.md`.

---

## A. Short V2 product goal

### What changes for the user compared to V1.5

- **Projects:** Scans can be grouped under a **named project** (client, site, initiative). The dashboard is **filterable by project**, and new scans can be **created with a project attached** so history is not only a flat list of scan UUIDs.
- **Compare to previous run:** After a **rescan**, the user can open a **before/after view** that contrasts two stored runs: scores (global / SEO / GEO), issues (resolved / new), and recommendations (persistent / new / dropped) — **derived from existing payloads**, not a new scoring engine.

### Why this V2 matters

- Matches **repeat real-world use**: same URL revisited over time, client/site workflows, invoice-friendly grouping.
- Delivers **iteration narrative** (`roadmap-v2-v3.md`): before/after without manually juggling two scan IDs in isolation.

### What problem it solves

- **Pile of UUIDs:** No lightweight structure to separate one client or site from another.
- **Opaque progress:** Hard to answer “did the last change improve anything?” without a dedicated comparison surface tied to **rescan lineage** (`parent_scan_id`).

---

## B. Exact V2 scope

### Projects — in practice

- **Create** named projects (per user).
- **List** projects (for picker / filter).
- **Assign at creation:** Optional `project_id` on **POST /api/scans** (must belong to the same user).
- **Filter history:** **GET /api/scans?project_id=** returns only scans for that project (same user).
- **No** workspaces, teams, RBAC, client portals, or shared project ownership.

### Compare to previous run — in practice

- **Lineage only:** **GET /api/scans/{scan_id}/compare** where `scan_id` is the **child** scan (the newer run) with **`parent_scan_id`** set (rescan). Response loads **parent + child** detail payloads and returns a **presentation diff** (issues by `code`, recommendations by `key` or normalized title, scores as stored per run).
- **No** arbitrary “pick any two scans” in short V2.
- **No** new composite delta score in the engine; UI may show numeric after − before as **presentation** only.

### User flows — **included**

1. Create a project from the dashboard; optionally stay filtered on that project.
2. Start a new scan **with** a project selected (dashboard) or **without** (all scans / landing unchanged).
3. Browse scan history; switch project filter; see empty state when a project has no scans.
4. Run **Rescan** on a completed (or existing) scan; open the **new** scan; open **Compare to previous run** (or dashboard link when the child row is settled).

### User flows — **excluded**

- Multi-URL bundles, rollup / site-wide scoring, sitemap crawl.
- Competitor URL compare, scheduled scans, rewrite assistance.
- App listing / ASO, billing, enterprise/workspace complexity.
- Reopening scoring calibration or changing ruleset versioning for this release slice.

---

## C. User stories

### Solo user

- **As a** solo builder, **I want to** tag scans with a simple project name, **so that** my experiments for different sites do not mix in one list.
- **As a** solo builder, **I want to** compare my latest rescan to the previous run, **so that** I can see score and issue movement without exporting two reports.

### Freelancer / agency user

- **As an** agency operator, **I want to** create one project per client (or per site), **so that** I can filter the dashboard before a check-in call.
- **As an** agency operator, **I want to** show before/after for a URL I fixed, **so that** I can ground the conversation in stored diagnostics, not anecdotes.

### SaaS / product user

- **As a** product marketer, **I want to** group scans for a key landing or pricing URL under a project, **so that** iterations across releases stay traceable.
- **As a** product marketer, **I want to** open a single compare view after a rescan, **so that** I can quickly see whether SEO/GEO scores and top issues moved in the expected direction.

---

## D. Screens / UX

| Surface | Role in short V2 |
|--------|-------------------|
| **Dashboard / history** | Load projects + scans; **project filter** (URL query optional); rows show status/scores; link to result; **“Compare runs”** when child has `parent_scan_id` and run is not in progress. |
| **Scan creation flow** | **Dashboard:** URL form submits with optional `project_id` when a valid project is selected. **Landing:** unchanged single-URL flow (no project required). |
| **Project-aware filtering / grouping** | Filter = **project_id** query param + API filter; **grouping** = single list filtered (no separate project detail page required for short V2). |
| **Compare page / section** | Dedicated route **/scan/{childId}/compare**; scores table + resolved/new issues + recommendation buckets; errors for non-rescan or unauthorized. |
| **Result page — Actions** | **“Compare to previous run”** when `meta.parent_scan_id` exists and the run is final and not failed (product choice: avoid compare CTA on failed final). |
| **Project-related empty states** | No scans in project; unknown/stale project id in URL; optional copy when filter is “all”. |
| **Compare-related empty/error states** | Loading; 401 with sign-in path; 404 / not a child rescan with explanatory copy; empty sections for zero resolved/new/rec deltas. |

---

## E. Backend / API scope

| Item | Short V2 expectation |
|------|----------------------|
| **Project model** | Table `projects` (user-scoped): `id`, `user_id`, `name`, `created_at`. |
| **Project creation / listing** | **POST /api/projects** `{ name }` → `ProjectRead`; **GET /api/projects** → list newest first. Auth: same user as JWT. |
| **Scan assignment** | **Optional `project_id`** on **POST /api/scans**; validate project exists and **belongs to user**; reject otherwise (4xx). **Rescan** copies parent’s `project_id` onto the child. |
| **Filtered scan history** | **GET /api/scans?project_id=&limit=** — returns scans for authenticated user, optionally restricted to that `project_id` (same semantics as unfiltered list regarding ownership). |
| **Compare endpoint** | **GET /api/scans/{child_scan_id}/compare** — child must exist, belong to user, have **`parent_scan_id`**; parent must exist and belong to same user; build **ScanCompareResponse** from stored detail payloads (**no scoring recomputation** for diff). |
| **Ownership / privacy** | All project and scan operations **scoped by `user_id`** from the session. Compare never crosses users. Public report behavior unchanged (out of scope for compare). |

---

## F. Frontend scope

| Required | Short V2 |
|----------|----------|
| **Dashboard** | Fetch **GET /api/projects** + **GET /api/scans** (with optional `project_id`); project create UI; filter synced to URL; pass `project_id` into scan create from dashboard. |
| **Compare** | Page at **/scan/[id]/compare**; client fetch **GET /api/scans/{id}/compare**; handle loading/error/empty buckets. |
| **Navigation** | Links from dashboard row and result **Actions** to compare when lineage exists. |
| **Types / API client** | Typed summaries including `project_id` / `parent_scan_id`; stable error handling for API failures (optional polish: structured `ApiError`). |

| Stay untouched (short V2) | Rationale |
|---------------------------|-----------|
| **Scoring pipeline, rules, calibration** | Frozen per `AGENTS.md`. |
| **Core single-URL result layout** (beyond compare CTA) | No redesign requirement. |
| **Public report contract** | Unchanged unless a bugfix. |
| **Billing / Stripe** | Explicitly out of scope. |

---

## G. Out of scope (anti-drift)

Do **not** implement under short V2 label without a **new** explicit phase:

- Multi-page bundles; rollup / site-wide scoring; full crawl or sitemap discovery.
- Compare **any** two arbitrary scans (only rescan child vs parent).
- Competitor comparison; scheduled scans; rewrite assistance.
- App listing / ASO; billing and plan gates; workspaces / RBAC / SSO.
- **Scoring engine / ruleset** changes beyond documented targeted fixes (not part of this slice).
- **Project management extras:** rename, delete, move scan between projects, archive (candidate for V2.5+).

---

## H. Acceptance criteria (short V2 “done”)

1. **Projects:** Authenticated user can create projects, see them listed, filter dashboard history by project, and create a new scan from the dashboard **with** that project attached; scans appear under the correct filter.
2. **Assignment integrity:** Invalid or other-user `project_id` on create is rejected with a clear client-visible error (no silent drop).
3. **Rescan lineage:** Rescan continues to set **`parent_scan_id`** on the child; child inherits **`project_id`** from parent where applicable.
4. **Compare:** For a valid child scan with parent, **GET /api/scans/{id}/compare** returns consistent before/after payloads; UI shows scores + issue/reco buckets; 404/401 paths do not crash the app.
5. **Discoverability:** User can reach compare from **dashboard** (settled rescan row) and from **result Actions** when lineage exists.
6. **No scoring drift:** No change to scoring version / ruleset versioning policy for this ship; compare remains presentation-only diff.
7. **Docs:** `api-design.md` describes projects, filtered list, and compare contract (integrator-accurate).

---

## I. Recommended implementation order

1. **Data + API contracts** — Project schemas; scan create accepts `project_id`; list scans accepts `project_id`; summaries expose `project_id` / `parent_scan_id`; compare response schema.
2. **Workflow implementation** — Postgres (and mock if used in CI) for list/create project, validate ownership on assign, implement `get_scan_compare` using existing detail builders + pure diff helper.
3. **Routes** — Register **GET/POST /api/projects**; wire **GET /api/scans** query; register **GET /api/scans/{id}/compare** before `{id}` detail route if path order matters.
4. **Frontend dashboard** — Projects fetch + filter + create project + scan form with optional `project_id`.
5. **Frontend compare** — Route + view consuming compare API; links from dashboard and result page.
6. **Edge polish** — Empty states, invalid `?project=` handling, API error messages, basic test on diff helper.
7. **Verification** — Manual: project filter → scan → rescan → compare; automated: unit test on presentation diff if feasible.

---

## J. Codebase map vs this frame (snapshot)

Use this to track drift; update when shipping.

| Area | Desired (frame) | Repo state |
|------|-------------------|------------|
| **GET/POST /api/projects** | Required | **Done** (`routes/projects.py`, workflow). |
| **POST /api/scans` + `project_id`** | Required + ownership validation | **Done** (workflow + 400 on bad id). |
| **GET /api/scans?project_id=`** | Required | **Done**. |
| **Summaries: `project_id`, `parent_scan_id`** | Required | **Done** (`scan_detail` / contracts). |
| **GET /api/scans/{id}/compare** | Required | **Done** (`scan_compare` + route). |
| **Rescan copies `project_id`** | Required | **Done** (postgres workflow rescan). |
| **Mock workflow parity** | CI / local mock | **Done** (mock supports projects + compare). |
| **Dashboard: projects + filter + create scan in project** | Required | **Done** (`DashboardScanHistory`). |
| **Landing scan without project** | Allowed | **Done** (unchanged path). |
| **Compare page + links** | Required | **Done** (`ScanCompareView`, `scan/[id]/compare`, `ResultShell`, dashboard row). |
| **`api-design.md`** | Aligned | **Done** (projects, filter, compare documented). |
| **Unit test for presentation diff** | Recommended | **Done** (`tests/test_scan_compare.py`). |
| **Assign existing scan to project (PATCH)** | Out of short V2 | **Missing** (by design). |
| **Project rename / delete / move scan** | Out of short V2 | **Missing** (by design). |
| **Compare two arbitrary scans** | Out of short V2 | **Missing** (by design). |
| **Backend: reject `project_id` on list if not owned** | Optional hardening | **Partial** — filter may return empty for foreign UUID without distinct 404 (acceptable for short V2). |
| **API error UX, invalid `?project=`, empty states** | Polish | **Done** / ongoing (`ApiError`, dashboard edge handling, compare error copy). |

---

*This frame supersedes informal scope for “short V2” when in conflict with the broad bullet list in `vision.md` §V2; product sequencing is authoritative in `roadmap-v2-v3.md`.*
