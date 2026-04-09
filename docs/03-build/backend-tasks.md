# Backend tasks

## Goal
Build the FastAPI backend for scan orchestration, extraction, scoring, and report delivery.

---

## Phase 1: foundation
- initialize FastAPI project structure
- configure environment loading
- configure database connection
- create base models and schemas
- add health route
- add basic logging

### Deliverables
- runnable FastAPI app
- database connection working
- project structure aligned with docs

---

## Phase 2: scan domain
- create Scan model
- create Project model
- create public report model
- create usage model
- implement POST /api/scans
- implement GET /api/scans/{scan_id}
- implement status lifecycle support

### Deliverables
- user can create a scan record
- user can poll scan status

---

## Phase 3: fetch and render
- implement URL normalization utility
- implement basic fetch service
- implement Playwright render service
- capture fetch diagnostics
- persist fetch/render result
- set failure and partial states properly

### Deliverables
- pipeline can retrieve public page content
- render diagnostics available

---

## Phase 4: extraction
- implement normalized extraction schema models
- parse meta tags
- parse headings
- parse content metrics
- parse links
- parse media
- parse structured data
- parse trust signals
- build derived metrics
- build llm payload candidate
- persist extraction payload

### Deliverables
- extraction object produced and stored for a scan

---

## Phase 5: page type detection
- implement page type heuristics
- compute page type confidence
- return candidate probabilities
- persist page detection values

### Deliverables
- scan contains page_type_detected and page_type_final

---

## Phase 6: deterministic scoring engine
- implement score pillar structure
- implement rule evaluation interface
- implement initial ruleset families
- implement issue generation
- implement recommendation mapping
- implement confidence computation
- persist score result

### Deliverables
- deterministic scores returned for a scan

---

## Phase 7: page type override
- implement PATCH /api/scans/{scan_id}/page-type
- recalculate score using existing extraction
- update page_type_final and score outputs

### Deliverables
- user can manually correct page type

---

## Phase 8: LLM layer
- implement provider-agnostic llm client interface
- implement prompt builder
- implement structured JSON parser
- integrate bounded LLM evaluation
- persist token/cost metadata
- fallback safely if provider fails

### Deliverables
- optional semantic analysis layer working without breaking deterministic engine

---

## Phase 9: public reports
- implement public report creation route
- implement public report retrieval route
- create safe public response serializer

### Deliverables
- scans can be shared via public URL

---

## Phase 10: rescans and comparisons
- implement POST /api/scans/{scan_id}/rescan
- support parent_scan_id
- compute scan deltas later or prepare backend structures

### Deliverables
- user can rerun analysis cleanly

---

## Phase 11: usage and billing hooks
- implement plan usage counters
- enforce quotas
- wire Stripe plan metadata if needed

### Deliverables
- basic billing-aware backend behavior

---

## Testing priorities
- URL normalization
- extraction schema generation
- page type detection
- rules triggering
- score aggregation
- confidence computation
- public report serialization