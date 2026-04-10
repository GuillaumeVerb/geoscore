
# GeoScore

GeoScore is a minimal SEO & GEO analyzer for websites and apps.

The product must stay extremely simple on the surface:
- one input URL
- one analysis flow
- one result page
- one clear score system

Under the hood, the product must be rigorous:
- deterministic rules are the core of scoring
- LLM is secondary and bounded
- scoring must be explainable
- every issue must map to a recommendation
- every result must expose limitations and confidence

## Core product idea

GeoScore answers one question:

"How ready is this page to rank, be understood, and be cited in modern search environments?"

The product outputs:
- Global Score
- SEO Score
- GEO Score
- page type
- confidence level
- strengths
- issues
- priority fixes

## Stack

- Frontend: Next.js on Vercel
- Backend: FastAPI on Railway
- Database: Postgres
- Rendering: Playwright
- Billing: Stripe
- Auth: lightweight auth
- LLM: provider-agnostic, low-cost by default

## Priority docs to read before coding

1. docs/00-product/vision.md
2. docs/01-architecture/architecture-overview.md
3. docs/01-architecture/api-design.md
4. docs/02-scoring/scoring-engine-v1.md
5. docs/02-scoring/rules-catalog-v1.md
6. docs/02-scoring/extraction-schema-v1.md
7. docs/02-scoring/llm-strategy.md
8. docs/03-build/implementation-roadmap.md

## Build priorities

1. scan submission flow
2. page fetch and render
3. extraction schema implementation
4. deterministic scoring engine
5. result API
6. minimal result UI
7. rescan flow
8. public report flow

## Non-negotiables

- Keep the UI minimal.
- Do not turn the product into a bloated SEO suite.
- Never make scoring black-box.
- Do not let LLM dominate the scoring logic.
- Always store scoring_version, ruleset_version, and prompt_version.
- **Scoring is frozen at `scoring-v1-cal03` / `ruleset-v1-cal03`.** Do not change the deterministic engine for broad re-calibration; only targeted fixes when a case is clearly wrong. Next improvement area: **partial scans** with strong limitations but little or no useful issues/recommendations — product/UX and rules at the margin, not a new global cal pass.
- Always expose limitations when analysis is partial.
- Page type detection must be visible and overridable by the user.
- Confidence must be shown in the result.
- Public reports must be clean and shareable.
- Cost per scan must remain bounded.

## Coding expectations

- Prefer clear, modular code over clever abstractions.
- Use typed schemas and explicit contracts.
- Keep services separated:
  - rendering
  - extraction
  - page type detection
  - scoring
  - llm analysis
  - reports
- Do not mix UI copy with backend scoring logic.
- Avoid large refactors unless explicitly requested.

## What to do when implementing a task

1. Read AGENTS.md
2. Read only the docs relevant to the current task
3. Restate the scope internally
4. Implement the smallest correct version
5. Keep naming aligned with the docs
6. Preserve versioning and explainability

## What not to do

- Do not invent features not in scope.
- Do not silently change scoring formulas.
- Do not collapse SEO and GEO into one opaque score.
- Do not add enterprise complexity too early.
- Do not ship output that hides uncertainty.