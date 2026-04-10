"""Version strings persisted with artifacts (AGENTS.md — versioning)."""

EXTRACTION_VERSION = "extraction-v1-rich"
# Bump when changing deterministic weights/thresholds (calibration passes)
SCORING_VERSION = "scoring-v1-cal03"
RULESET_VERSION = "ruleset-v1-cal03"
# LLM not used; kept null on scan rows
LLM_PROMPT_VERSION_PLACEHOLDER = None

FETCH_METHOD_HTTP = "http_get"
# HTTP succeeded; Playwright render replaced HTML for extraction
FETCH_METHOD_HTTP_THEN_PLAYWRIGHT = "http_then_playwright"
# Playwright ran but HTTP snapshot kept for extraction (failure or weak gain)
FETCH_METHOD_HTTP_PLAYWRIGHT_ATTEMPTED = "http_playwright_attempted"
RENDER_ENGINE_PLAYWRIGHT = "playwright_chromium"
RENDER_ENGINE_NONE = "none"
