# MVP checklist

## Product
- [ ] One clear homepage with URL input
- [ ] One scan flow from submission to result
- [ ] One result page with scores and fixes
- [ ] Product remains simple and focused

## Backend
- [ ] FastAPI app bootstrapped
- [ ] Postgres connected
- [ ] Scan creation works
- [ ] Scan status retrieval works
- [ ] Fetch/render pipeline works
- [ ] Extraction schema is produced
- [ ] Page type is detected
- [ ] Deterministic scoring works
- [ ] Issues are generated
- [ ] Recommendations are mapped
- [ ] Confidence is computed
- [ ] Rescan endpoint works
- [ ] Public report endpoint works

## Frontend
- [ ] Landing page works
- [ ] URL submission works
- [ ] Loading/polling states work
- [ ] Result page works
- [ ] Partial/failed states are visible
- [ ] Page type override works
- [ ] Rescan flow works
- [ ] Public report page works

## Scoring
- [ ] Global score computed
- [ ] SEO score computed
- [ ] GEO score computed
- [ ] Main sub-scores computed
- [ ] Ruleset version stored
- [ ] Scoring version stored
- [ ] Confidence shown
- [ ] Limitations shown

## LLM
- [ ] LLM is optional, not required for a valid scan
- [ ] LLM payload is normalized and bounded
- [ ] LLM output is structured
- [ ] LLM failure reduces confidence, not system stability

## Public report
- [ ] Shareable public URL exists
- [ ] Public report hides private/internal fields
- [ ] Public report shows scores, page type, confidence, issues, fixes

## Billing/usage
- [ ] Usage is tracked
- [ ] Free plan limits enforced
- [ ] Upgrade path visible

## Quality
- [ ] Scoring is explainable
- [ ] UI remains minimal
- [ ] No black-box behavior
- [ ] No silent partial analysis
- [ ] Naming matches docs