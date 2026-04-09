# Pipeline analysis

## Goal
Describe the full analysis lifecycle from URL submission to final report.

## Core pipeline
1. submission
2. normalization
3. fetch/render
4. extraction
5. page type detection
6. deterministic scoring
7. optional LLM semantic analysis
8. aggregation
9. persistence
10. delivery

---

## 1. Submission

### Input
- URL
- optional project_id
- optional page_type_override

### Responsibilities
- validate input
- normalize URL
- check user quota
- create scan record
- set initial status

### Output
- scan_id
- queued status

---

## 2. Normalization

### Responsibilities
- clean URL format
- normalize scheme and trailing slash rules
- extract domain and path
- prepare canonical internal representation

### Why it matters
Scans should compare like-for-like and avoid duplicate variants.

---

## 3. Fetch / render

### Strategy
Use the lightest viable method first, then escalate if needed.

### Recommended flow
- attempt lightweight fetch
- if content is insufficient or heavily dynamic, use Playwright render

### Responsibilities
- capture HTTP status
- follow redirects
- detect probable auth wall
- detect probable bot block
- capture final URL
- measure render success

### Possible outputs
- full render
- partial render
- failed render

---

## 4. Extraction

### Responsibilities
Build a normalized extraction object from DOM/content.

### Main extraction domains
- meta
- headings
- content
- links
- media
- structured data
- trust signals
- page features
- derived metrics
- limitations
- llm payload candidate

### Important rule
Extraction should convert raw content into structured, reusable signals.
Do not score directly from raw HTML.

---

## 5. Page type detection

### Purpose
Detect which scoring context applies.

### Main page types
- homepage
- landing_page
- product_page
- pricing_page
- article
- about_page
- app_page
- other

### Inputs
- URL path
- title
- headings
- structural clues
- lexical patterns
- content shape

### Output
- page_type_detected
- page_type_confidence
- candidate probabilities

### Product requirement
The user must be able to override detected page type.

---

## 6. Deterministic scoring

### Purpose
Compute most of the final score using explicit rules.

### Score families
#### SEO
- technical basics
- on-page structure
- content signals
- discoverability

#### GEO
- clarity of intent
- extractability
- citation readiness
- entity trust

### Outputs
- sub-scores
- triggered rules
- initial issues
- initial score adjustments

---

## 7. Optional LLM semantic analysis

### Purpose
Refine the qualitative side of GEO and summary generation.

### Inputs
A bounded normalized payload, not full raw HTML.

### Responsibilities
- judge clarity
- judge extractability
- judge citation readiness
- judge entity trust
- enrich summary
- enrich recommendation wording

### Constraints
- bounded token budget
- structured JSON output
- provider-agnostic
- failure should not break deterministic scoring

---

## 8. Aggregation

### Purpose
Merge all analysis layers into one coherent report.

### Responsibilities
- compute final SEO score
- compute final GEO score
- compute global score
- merge issues
- deduplicate overlaps
- map issues to recommendation groups
- compute confidence
- attach limitations

### Output
Final report object.

---

## 9. Persistence

### Persist
- scan metadata
- fetch/render result
- normalized extraction
- scores
- issues
- recommendations
- LLM metadata if used
- public report record if created

---

## 10. Delivery

### Private scan result
Return:
- status
- page type
- confidence
- scores
- strengths
- issues
- recommendations
- limitations

### Public report
Return a reduced, shareable view:
- URL
- date
- page type
- confidence
- scores
- top issues
- top fixes

---

## Analysis states

### Completed
All major stages succeeded.

### Partial
Enough content was extracted to produce a useful but limited result.

### Limited
The page was analyzed with major constraints; caution is required.

### Failed
The page could not be analyzed reliably.

---

## Error classes
- invalid URL
- network timeout
- redirect issue
- render failure
- blocked/protected page
- content too thin
- extraction failure
- LLM unavailable
- quota exceeded

---

## Confidence inputs
Confidence should consider:
- render success
- content completeness
- extraction richness
- page type certainty
- limitations
- LLM validity if used

---

## Future evolutions
- multi-page crawl
- scheduled scans
- competitor scans
- benchmark overlays
- rewrite suggestions