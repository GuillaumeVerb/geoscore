# Database schema

## Goal
Persist scans, extractions, scores, issues, recommendations, public reports, and usage.

## Design principles
- keep the initial schema simple
- make scans the central object
- version extracted/scored artifacts
- separate raw analysis artifacts from user-facing summaries

---

## Table: users

### Purpose
Account owner of scans and projects.

### Suggested fields
- id (uuid, pk)
- email (text, unique)
- created_at (timestamptz)
- plan_id (text)
- stripe_customer_id (text, nullable)
- is_active (boolean)

---

## Table: projects

### Purpose
Logical grouping for scans. A project can map to a site, client, brand, or app.

### Suggested fields
- id (uuid, pk)
- user_id (uuid, fk users.id)
- name (text)
- created_at (timestamptz)

---

## Table: scans

### Purpose
Main lifecycle object for one analysis run.

### Suggested fields
- id (uuid, pk)
- user_id (uuid, fk users.id)
- project_id (uuid, nullable, fk projects.id)
- parent_scan_id (uuid, nullable, fk scans.id)
- submitted_url (text)
- normalized_url (text)
- final_url (text, nullable)
- domain (text)
- path (text)
- status (text)
- analysis_mode (text, default standard)
- scan_trigger (text, default manual)
- page_type_detected (text, nullable)
- page_type_final (text, nullable)
- page_type_confidence (numeric, nullable)
- analysis_confidence (text, nullable)
- extraction_version (text, nullable)
- scoring_version (text, nullable)
- ruleset_version (text, nullable)
- llm_prompt_version (text, nullable)
- limitations (jsonb, nullable)
- error_code (text, nullable)
- error_message (text, nullable)
- created_at (timestamptz)
- started_at (timestamptz, nullable)
- completed_at (timestamptz, nullable)

### Notes
- `parent_scan_id` supports rescans and comparisons
- `page_type_final` can differ from `page_type_detected` if the user overrides it

---

## Table: scan_fetch_results

### Purpose
Store fetch/render layer outputs and diagnostics.

### Suggested fields
- id (uuid, pk)
- scan_id (uuid, fk scans.id)
- http_status (int, nullable)
- fetch_method (text)
- render_success (boolean)
- final_url (text, nullable)
- content_type (text, nullable)
- page_title (text, nullable)
- html_size (int, nullable)
- main_text_size (int, nullable)
- load_time_ms (int, nullable)
- is_probably_spa (boolean, nullable)
- is_blocked (boolean, nullable)
- has_auth_wall (boolean, nullable)
- created_at (timestamptz)

---

## Table: scan_extractions

### Purpose
Persist normalized extraction objects.

### Suggested fields
- id (uuid, pk)
- scan_id (uuid, fk scans.id)
- extraction_version (text)
- extraction_payload (jsonb)
- created_at (timestamptz)

### Notes
For V1, one JSONB payload is simpler than spreading extraction across many relational tables.

---

## Table: scan_scores

### Purpose
Persist final scores and sub-scores.

### Suggested fields
- id (uuid, pk)
- scan_id (uuid, fk scans.id)
- scoring_version (text)
- ruleset_version (text)
- global_score (numeric)
- seo_score (numeric)
- geo_score (numeric)
- seo_subscores (jsonb)
- geo_subscores (jsonb)
- penalties (jsonb)
- bonuses (jsonb)
- confidence_score (numeric, nullable)
- created_at (timestamptz)

---

## Table: scan_issues

### Purpose
Persist normalized issues shown in reports.

### Suggested fields
- id (uuid, pk)
- scan_id (uuid, fk scans.id)
- code (text)
- title (text)
- description (text)
- severity (text)
- impact_scope (text)
- evidence (jsonb)
- fix_priority (int)
- created_at (timestamptz)

---

## Table: scan_recommendations

### Purpose
Persist normalized recommendations shown in reports.

### Suggested fields
- id (uuid, pk)
- scan_id (uuid, fk scans.id)
- key (text, nullable)
- title (text)
- explanation (text)
- impact_scope (text)
- priority (int)
- effort (text)
- expected_gain (text)
- created_at (timestamptz)

---

## Table: scan_llm_outputs

### Purpose
Auditability and cost tracking for the LLM layer.

### Suggested fields
- id (uuid, pk)
- scan_id (uuid, fk scans.id)
- llm_provider (text)
- model (text)
- prompt_version (text)
- input_payload (jsonb)
- output_payload (jsonb)
- token_input (int, nullable)
- token_output (int, nullable)
- cost_estimate (numeric, nullable)
- created_at (timestamptz)

### Notes
This is useful for benchmarking providers and tracking cost drift.

---

## Table: public_reports

### Purpose
Expose a public shareable version of a scan.

### Suggested fields
- id (uuid, pk)
- scan_id (uuid, fk scans.id)
- public_id (text, unique)
- is_enabled (boolean, default true)
- created_at (timestamptz)

---

## Table: plan_usage

### Purpose
Track monthly usage for quotas and billing logic.

### Suggested fields
- id (uuid, pk)
- user_id (uuid, fk users.id)
- month_key (text)
- scans_used (int, default 0)
- rescans_used (int, default 0)
- pdf_exports_used (int, default 0)
- created_at (timestamptz)

---

## Suggested indexes
- scans.user_id
- scans.project_id
- scans.status
- scans.domain
- scans.created_at
- public_reports.public_id
- plan_usage.user_id + month_key

---

## V1 simplification choices
To move fast:
- keep extraction as a single JSONB payload
- keep sub-scores as JSONB
- keep limitations as JSONB
- avoid over-normalizing early

## V2 possible evolutions
- historical score snapshots per page key
- benchmark tables
- team/workspace tables
- scheduled scan tables
- API key tables