# Extraction schema V1

## Purpose
The extraction schema is the normalized data object produced by the extraction pipeline.

It is the source input for:
- deterministic scoring
- page type detection
- LLM payload generation
- reports

## Main top-level sections
- schema_version
- scan_id
- url_info
- fetch_info
- render_info
- page_detection
- meta
- headings
- content
- links
- media
- structured_data
- trust_signals
- page_features
- derived_metrics
- limitations
- llm_payload_candidate

## Principle
Do not score directly from raw HTML.
Score from normalized extracted signals.