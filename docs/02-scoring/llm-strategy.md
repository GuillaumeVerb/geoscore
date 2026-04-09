# LLM strategy

## Principle
GeoScore must be LLM-agnostic.

## Role of LLM
The LLM layer is used for:
- clarity evaluation
- extractability evaluation
- citation-readiness evaluation
- entity-trust evaluation
- short summary generation
- recommendation enrichment

## What LLM must not do
- own the scoring logic
- read full raw HTML by default
- return long unstructured prose
- silently override deterministic results

## Token budget policy
Use a bounded normalized payload:
- title
- meta description
- hero
- headings
- main excerpt
- structural feature flags
- trust signal summary
- limitations

## Cost policy
Default provider should be low-cost.
Premium providers can be used for premium modes or internal QA.

## Fallback policy
If LLM is unavailable:
- analysis still completes if deterministic extraction is sufficient
- confidence is reduced
- limitations are surfaced