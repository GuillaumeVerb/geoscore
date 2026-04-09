# API design

## Main routes

### POST /api/scans
Create a scan from a URL.

### GET /api/scans/{scan_id}
Return scan status and result.

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