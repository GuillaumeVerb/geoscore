# API design

## Operational (no auth)

### GET /health
Liveness: API process is running. Always **200** with `{"status":"ok"}` when the server accepts the request.

### GET /ready
Readiness: dependency check for deploy orchestrators.
- When **`USE_MOCK_WORKFLOW=true`**: **200**, `database: skipped`, `workflow: mock` (no Postgres required).
- When **`USE_MOCK_WORKFLOW=false`**: **200** if `SELECT 1` against `DATABASE_URL` succeeds; **503** if the database is unreachable.

## Main routes

### GET /api/projects
List projects for the signed-in user (newest first).

### POST /api/projects
Create a project (`{ "name": string }`). Returns the created project row.

### POST /api/scans
Create a scan from a URL. Optional body field **`project_id`** (UUID) attaches the scan to a project owned by the user.

### GET /api/scans
List recent scans for the user. Optional query **`project_id`** filters to scans in that project.

### GET /api/scans/{scan_id}
Return scan status and result.

### GET /api/scans/{scan_id}/compare
Before/after presentation for a **rescan**: **`scan_id`** must be the **child** scan with **`parent_scan_id`** set. Returns parent/child ids, submitted URL, **`before_scores`** / **`after_scores`** (global, SEO, GEO), **`resolved_issues`**, **`new_issues`** (by issue `code`), and recommendation buckets **`recommendations_persistent`**, **`recommendations_new`**, **`recommendations_removed`** (matched by recommendation `key` or normalized `title`). No separate scoring delta engine — differences are derived from the two stored payloads.

### POST /api/scans/{scan_id}/rescan
Create a new scan from an existing one.

### PATCH /api/scans/{scan_id}/page-type
Override page type and recalculate scoring.

### POST /api/scans/{scan_id}/public-report
Generate or enable a public report.

### GET /api/public-reports/{public_id}
Return a public report.

## Status lifecycle
- created
- queued
- fetching
- rendering
- extracting
- scoring_rules
- scoring_llm
- aggregating
- completed
- partial
- failed

## Result payload essentials
- scan_id
- status
- page_type_detected
- page_type_final
- analysis_confidence
- global_score
- seo_score
- geo_score
- strengths
- issues
- recommendations
- limitations