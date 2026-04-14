# Short V2 — execution plan (sprints)

**Scope lock:** **Projects** + **Compare to previous run** only.  
**Frozen:** `scoring-v1-cal03` / `ruleset-v1-cal03` — no scoring engine or ruleset reopen.  
**Out of this plan:** multi-page bundle, rollup, competitor, scheduled scans, rewrite assist, app/ASO, billing, enterprise/RBAC.  
**Authority:** `AGENTS.md`, `docs/00-product/roadmap-v2-v3.md`, `docs/00-product/positioning.md`.

---

## A. Short V2 target

**“Done”** means: an authenticated user can **create and list projects**, **attach new scans to a project** (optional), **filter the dashboard history by project**, and **open a before/after compare view** for any **child scan** that has a **`parent_scan_id`** (rescan lineage). Compare shows **global / SEO / GEO** scores from each stored run, **resolved vs new issues** (by `code`), and **recommendation buckets** (persistent / new / removed) derived **only** from existing scan payloads — **no** new scoring or delta engine. Mock workflow (`USE_MOCK_WORKFLOW=true`) and Postgres workflow both behave consistently enough for **CI + manual smoke**. `docs/01-architecture/api-design.md` matches shipped routes. No new product pillars beyond **repeatability** and **iteration narrative**.

---

## B. Sprint plan (4 sprints)

### Sprint 1 — **Projects (backend)**

1. **Sprint name:** Projects API & persistence  
2. **Sprint goal:** User-scoped projects are creatable and listable; scans can persist `project_id` with ownership validation.  
3. **Backend scope:**  
   - Ensure `projects` table + `scans.project_id` FK path matches `database-schema.md`.  
   - Implement or verify: **`GET /api/projects`**, **`POST /api/projects`** (name validation, `user_id`).  
   - Extend **`POST /api/scans`**: optional `project_id`; **400** if UUID invalid or project not owned by user.  
   - Extend **`GET /api/scans`**: optional **`project_id`** query; summaries include **`project_id`** (and **`parent_scan_id`** if not already) for dashboard.  
   - **`ScanWorkflowPort`** + **Postgres** + **Mock** implementations aligned (mock must filter list by `project_id` for CI/UI without DB).  
4. **Frontend scope:** None (API-only sprint).  
5. **UX/product scope:** None beyond API error shapes (`detail` strings) suitable for UI.  
6. **Acceptance criteria:**  
   - Authenticated `POST /api/projects` returns **201** + body with `id`, `name`, `created_at`.  
   - `GET /api/projects` returns only the caller’s projects, newest first.  
   - `POST /api/scans` with valid `project_id` persists association; invalid/other-user id → **400**.  
   - `GET /api/scans?project_id=` returns only matching scans for that user.  
   - Mock mode: same contracts hold for manual/CI smoke.  
7. **Explicit non-goals:** Project rename/delete; PATCH scan to move project; project detail page; billing; any scoring change.  
8. **Dependencies / sequencing:** Requires existing auth + scan create path; no dependency on compare.

---

### Sprint 2 — **Compare to previous run (backend)**

1. **Sprint name:** Rescan compare API  
2. **Sprint goal:** A single authenticated endpoint returns a **presentation diff** between parent and child scans for valid rescan lineage.  
3. **Backend scope:**  
   - Implement or verify **`GET /api/scans/{scan_id}/compare`** registered **before** `GET /api/scans/{scan_id}` if path order matters in the router.  
   - Load **child** by id; require **`child.parent_scan_id`**; load **parent**; both **`user_id`** must match caller.  
   - Reuse existing detail builders (**`scan_to_detail_response`** or equivalent) for parent and child; call **`build_scan_compare`** (pure diff: issues by `code`, recos by `key`/normalized title, scores from payloads).  
   - Response schema: **`ScanCompareResponse`** (parent/child ids, `submitted_url`, `before_scores` / `after_scores`, issue lists, reco buckets).  
   - **404** (or consistent `Scan not found`) when child missing, wrong user, or no `parent_scan_id`.  
   - Unit test: **`build_scan_compare`** with synthetic parent/child **`ScanDetailResponse`** (no DB).  
4. **Frontend scope:** None.  
5. **UX/product scope:** None; ensure JSON field names match what the UI will consume.  
6. **Acceptance criteria:**  
   - For a real rescan pair in dev DB, compare returns coherent before/after blocks.  
   - Opening compare on a scan **without** parent → **404** + stable `detail`.  
   - No new tables; no scoring pipeline changes.  
7. **Explicit non-goals:** Compare arbitrary two scans; competitor compare; recomputing scores; changing `parent_scan_id` semantics on rescan.  
8. **Dependencies / sequencing:** Depends on **reliable `ScanDetailResponse`** for completed/partial runs; independent of Sprint 1 **if** rescan already exists without projects.

---

### Sprint 3 — **Projects (frontend)**

1. **Sprint name:** Dashboard project UX  
2. **Sprint goal:** User can create a project, filter history by project, and start a scan **into** the selected project from the dashboard.  
3. **Backend scope:** Bugfixes only if Sprint 1 acceptance gaps found.  
4. **Frontend scope:**  
   - Dashboard: fetch **`GET /api/projects`** + **`GET /api/scans`** (with optional `project_id`).  
   - UI: create project (name), project **filter** (sync to **`?project=`** query optional but recommended).  
   - Extend **`UrlSubmitForm`** (or dashboard-only wrapper): **`POST /api/scans`** body includes **`project_id`** when a valid project is selected.  
   - Types: **`ScanSummary`** includes `project_id?`, `parent_scan_id?`; project type aligned with API.  
   - **`Suspense`** boundary if `useSearchParams` is used on dashboard (Next.js App Router).  
5. **UX/product scope:**  
   - Copy: short explanation that projects group scans (client/site), optional.  
   - Empty states: no scans in project vs no scans at all.  
   - Invalid/stale `?project=` handling (strip URL or banner + clear filter) — minimal, no new screens.  
6. **Acceptance criteria:**  
   - User can create project → land or stay on filtered view → submit URL → new scan appears under filter.  
   - “All scans” shows unfiltered list.  
   - Unauthenticated redirect behavior unchanged for scan create.  
7. **Explicit non-goals:** Landing page project picker (optional later); multi-page upload; rollup; project settings page.  
8. **Dependencies / sequencing:** Requires Sprint **1** APIs stable.

---

### Sprint 4 — **Compare (frontend) + release hardening**

1. **Sprint name:** Compare UI & short V2 release  
2. **Sprint goal:** User discovers and uses compare from **dashboard** and **scan result**; errors are understandable; docs and release checklist updated.  
3. **Backend scope:** Only fixes uncovered by E2E (compare ownership edge cases, etc.).  
4. **Frontend scope:**  
   - Route **`/scan/[id]/compare`** (client component acceptable): **`GET /api/scans/{id}/compare`**.  
   - UI: scores table (before / after / simple change column is **presentation**, not new engine), resolved/new issues, reco buckets; loading + **401** / **404** states.  
   - **Dashboard:** link **“Compare runs”** (or equivalent) on rows where **`parent_scan_id`** exists and status is not in-progress (product rule as agreed).  
   - **Result page (`ResultShell`):** **“Compare to previous run”** when **`meta.parent_scan_id`** present and compare is meaningful (e.g. final, not failed — match product choice).  
5. **UX/product scope:**  
   - Crumb/nav: back to dashboard + parent/child scan links as needed.  
   - Copy: clarify compare is **rescan-only**, presentation diff.  
6. **Acceptance criteria:**  
   - Full manual path: scan → rescan → open child → compare shows parent vs child data.  
   - Dashboard path: settled child row → compare page works.  
   - **401** prompts sign-in where applicable; **404** explains non-rescan.  
   - **`api-design.md`** lists projects, filtered scans, compare.  
   - **`npx tsc --noEmit`** + **`pytest`** green on CI paths you rely on.  
7. **Explicit non-goals:** Public compare URL; email notifications; exporting compare PDF; any billing gate; scoring or ruleset edits.  
8. **Dependencies / sequencing:** Requires Sprints **2** and **3** (or at least **2** + minimal list showing `parent_scan_id`); dashboard links nicer after **3**.

---

## C. Suggested sprint order

**Order: 1 → 2 → 3 → 4.**

- **Backend-first (1 then 2):** locks **contracts** and error semantics before UI work; frontend can mock against stable OpenAPI/JSON shapes.  
- **Compare backend (2) after Projects (1):** small team warms up on the simpler surface first; compare remains **logically independent** but benefits from the same **scan summary** fields (`parent_scan_id`) delivered in **1**.  
- **Frontend Projects (3) before Compare UI (4):** dashboard becomes the **home** for project context; compare links naturally sit beside filtered history.  
- **Compare UI last (4):** integrates **navigation** from both dashboard and result page and closes with **docs + release criteria** in one pass.

*If two developers parallelize: **1** and **2** can overlap only after port/router contracts are agreed; **3** still waits **1**; **4** waits **2** and ideally **3**.*

---

## D. Risks and guardrails

| Risk | Mitigation |
|------|------------|
| **Scope creep** | Any request for “pick two scans”, “project rename”, “bundle”, “rollup”, “export compare” during these sprints → log to **later V2 / V3** backlog; do not merge under short V2. |
| **Scoring drift** | No tickets that touch **`score_minimal.py`**, rules catalog calibration, or “just one small weight tweak” — **frozen** per `AGENTS.md`. |
| **Compare becomes a new engine** | **Code review:** compare module only **diffs** stored issues/recos/scores; reject PRs that add composite “delta score” persistence. |
| **Billing-shaped sequencing** | Do not tie sprints to Stripe, plan tiers, or “we must ship limits first” — soft limits are **not** in short V2. |
| **Enterprise hooks** | No `workspace_id`, no RBAC tables, no shared projects — reject in review. |

---

## E. Release criteria for short V2

Short V2 is **complete** when all are true:

1. **Projects:** Create + list + filter + assign-at-create works in **Postgres** workflow; **mock** workflow does not regress CI.  
2. **Compare:** Child-with-parent compare works end-to-end; invalid cases return **safe** HTTP errors and UI does not crash.  
3. **Navigation:** User can reach compare from **dashboard** (when lineage + status rules pass) and from **scan result** (when `parent_scan_id` in meta and product rules pass).  
4. **Documentation:** `api-design.md` reflects **`/api/projects`**, **`GET /api/scans?project_id`**, **`GET /api/scans/{id}/compare`**, and scan create **`project_id`**.  
5. **Quality gate:** CI (or agreed local checklist) — backend tests including compare diff unit test; frontend typecheck/lint per repo standards.  
6. **Positioning intact:** No new primary surfaces that contradict “one URL in, one result out” for the **default** path; projects/compare are **additive**, not a suite rewrite.

---

## F. Nice-to-have but not now

Defer explicitly (do not schedule inside short V2 sprints):

- Multi-page bundle (3–7 URLs), rollup / site snapshot  
- Competitor comparison, scheduled scans, rewrite assistance  
- App listing / ASO, trends / BI-style history  
- Billing / plans as **product** milestone; enterprise / workspaces / RBAC  
- Project rename, delete, move scan between projects  
- Compare any two arbitrary scans; public share of compare  
- Broad scoring recalibration (remains **frozen** until a separate, explicit decision outside short V2)

---

*This document is the execution companion to `docs/00-product/short-v2-projects-compare-frame.md` and `docs/00-product/feature-prioritization-matrix.md`.*
