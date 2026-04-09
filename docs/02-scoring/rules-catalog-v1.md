# Rules catalog V1

This file contains the full rule catalog for GeoScore V1.

## Main families
- SEO technical basics
- SEO on-page structure
- SEO content signals
- SEO discoverability
- GEO clarity of intent
- GEO extractability
- GEO citation readiness
- GEO entity trust
- cross-scope rules
- confidence and limitation rules

## Rule model
Each rule should define:
- code
- title
- category
- scope
- severity
- weight
- applies_to
- condition
- evidence_fields
- recommendation_key

## Notes
- use bounded penalties
- avoid duplicate punishment from highly correlated rules
- keep page-type-aware weighting
- keep recommendation mapping compact