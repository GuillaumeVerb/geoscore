# Frontend tasks

## Goal
Build a minimal, clean Next.js frontend for URL submission, result display, rescans, and public reports.

---

## Phase 1: app shell
- initialize Next.js app
- set base layout
- add top-level navigation
- set typography and spacing system
- create minimal design primitives

### Deliverables
- clean app shell
- stable page structure

---

## Phase 2: landing page
- create home page
- add URL input form
- add validation
- add call-to-action
- add short supporting copy
- wire submission to backend

### Deliverables
- user can submit a URL

---

## Phase 3: loading and scan state
- create scan status state handling
- create loading screen
- create polling logic
- handle queued/running/completed/partial/failed states

### Deliverables
- user sees progress and result states clearly

---

## Phase 4: result page
- create score header
- show global score
- show SEO score
- show GEO score
- show page type
- show confidence
- show summary
- show strengths
- show issues
- show recommendations
- show limitations

### Deliverables
- result page reflects the full scan output

---

## Phase 5: page type override
- create editable page type control
- call override endpoint
- refresh scoring result after change

### Deliverables
- user can correct page type from the UI

---

## Phase 6: partial and failed states
- create partial analysis banner
- create limited analysis messaging
- create failed analysis screen
- make tone cautious when needed

### Deliverables
- uncertainty is visible and well communicated

---

## Phase 7: rescan flow
- add rescan action
- show prior scan reference if relevant
- refresh into new result page

### Deliverables
- user can rescan after fixes

---

## Phase 8: public report flow
- add share action
- show public report URL
- create public report page
- strip private/internal details from public view

### Deliverables
- user can share a clean public result

---

## Phase 9: dashboard/history
- create scans history page
- list recent scans
- group by project if available
- support navigation to prior results

### Deliverables
- user has a usable history view

---

## Phase 10: pricing and usage
- create pricing page
- show plan information
- show current usage summary in app
- wire upgrade CTA

### Deliverables
- product is ready for gated usage

---

## UI priorities
- minimal visual complexity
- readable score header
- clear hierarchy
- visible limitations
- no dashboard clutter

## Components to build
- UrlSubmitForm
- ScanStatusCard
- ScoreHeader
- SummaryCard
- StrengthsList
- IssuesList
- RecommendationsList
- LimitationsBanner
- PageTypeSelector
- ShareReportCard
- RescanButton