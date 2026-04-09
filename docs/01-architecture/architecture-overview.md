# Architecture overview

## Stack
- Next.js frontend
- FastAPI backend
- Postgres database
- Playwright rendering
- provider-agnostic LLM layer
- Stripe for billing

## Main pipeline
1. submit URL
2. normalize URL
3. fetch or render page
4. extract normalized signals
5. detect page type
6. compute deterministic scores
7. optionally run LLM semantic analysis
8. aggregate final report
9. persist report
10. return result

## Design principles
- modular services
- deterministic scoring first
- bounded LLM usage
- visible confidence
- explicit limitations
- clean public reports

## Key objects
- scan
- extraction
- score
- issue
- recommendation
- public report