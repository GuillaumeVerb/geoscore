# Calibration (scores, issues, recommendations)

## Goal

Evaluate GeoScore on **real pages** before adding LLM, queues, or heavier infra. This doc describes the **corpus**, how to **run the batch**, what we watch for, and **cal-01** adjustments applied to the deterministic engine.

## Corpus (`backend/calibration/corpus.json`)

| id | category | URL |
|----|----------|-----|
| saas_home_stripe | homepage_saas | https://stripe.com |
| saas_home_vercel | homepage_saas | https://vercel.com |
| landing_linear | landing_modern | https://linear.app |
| pricing_stripe | pricing | https://stripe.com/pricing |
| pricing_notion | pricing | https://www.notion.so/pricing |
| product_page_slack | product | https://slack.com/features |
| article_mozilla | article | https://blog.mozilla.org/en/mozilla/mozilla-news/ |
| article_cloudflare | article | https://blog.cloudflare.com/welcome-to-cve-2024-6387/ |
| about_github | about | https://github.com/about |
| about_atlassian | about | https://www.atlassian.com/company |
| docs_react | js_heavy_docs | https://react.dev |
| docs_nextjs | js_heavy_docs | https://nextjs.org/docs |
| marketing_hubspot | marketing_long | https://www.hubspot.com |
| ecom_shopify | homepage_saas | https://www.shopify.com |
| news_bbc | article_news | https://www.bbc.com/news |
| app_web_twitter | js_heavy_app | https://x.com |

**Note:** Some hosts block or challenge bots; offline runs reflect **HTTP-only** capture unless you use **API mode** with Playwright fallback. Re-run failed rows manually or swap URLs.

## Run the calibration script

From `backend/`:

```bash
# Quick pass: HTTP + extract + score (no DB, no Playwright)
PYTHONPATH=. python scripts/run_calibration.py --mode offline --out-dir calibration/out

# Full pipeline (requires Postgres + uvicorn; includes optional Playwright)
PYTHONPATH=. python scripts/run_calibration.py --mode api --base http://127.0.0.1:8000 --out-dir calibration/out
```

Outputs (timestamped):

- `calibration/out/calibration_<UTC>.json` — full payload per row + heuristics; each row includes **`validation_context`** (page types, `fetch_method`, `partial`, `is_probably_spa`, `pipeline_context`, word/heading/link counts, `has_faq` / `has_examples` / `has_numbers`, `limitations_top`)
- `calibration/out/calibration_<UTC>.md` — summary table + per-page context lines + top issues/recs + frequency tables

### Heuristics (automated flags)

The script aggregates:

- **issue_code_frequency** / **recommendation_key_frequency** — spot redundant catalog noise
- **row_flags** — e.g. `many_issues` (≥9), `very_low_global` (&lt;38), `high_score_partial`

Use these as **starting points** for human review, not ground truth.

## What to review manually

Per page type, ask:

1. **Scores** — Does global/SEO/GEO match intuitive quality vs competitors in the same row?
2. **Issues** — False positives? (e.g. meta description when OG is fine; internal links on client-routed SPAs)
3. **Recommendations** — Same `key` repeating for different symptoms? Wording actionable?
4. **Limitations** — Partial/fallback messages aligned with real capture quality?
5. **Confidence** — Too high on thin or partial captures?

Document findings in a new run’s Markdown export or in PR notes.

## Anomalies often seen (before cal-01)

- **Correlated rules:** `META_DESC_MISSING` + weak SEO title_meta; `IMPROVE_HEADING_STRUCTURE` from H1 + H2 rules
- **Too severe:** Internal link nags on SPAs; FAQ nags on editorial longform; JSON-LD nags on short pages
- **Too permissive:** Thin heroes still scoring high on brand homepages (watch `hero_clarity` vs manual judgment)
- **Repetition:** `REWRITE_HERO` / `CLARIFY_OFFER_POSITIONING` sharing triggers — dedupe keys already limit noise; wording still overlaps

## Adjustments applied: ruleset/scoring **v1-cal01**

Version strings: `ruleset-v1-cal01`, `scoring-v1-cal01` (see `backend/app/services/pipeline/constants.py`).

| Area | Change |
|------|--------|
| Meta | If `meta_description` empty but **OG description ≥ 45 chars** or **twitter:card** set → treat as partial substitute (`desc_score` 72, strength line); **no** `META_DESC_MISSING`. Else issue severity **medium**, priority **2** (was high/1) |
| Title length | “Long title” threshold **70** chars (was 66) |
| H2 on long page | Only if **word_count > 520** (was 420) |
| Internal links | Flag if **words > 300** and **internal < 2** (was 220 / &lt;3) |
| Hero shallow | Commercial **hero &lt; 22** words (was 28) |
| Hero CTA | Only if hero **> 28** words without CTA (was 15) |
| Offer clarity | Commercial **words > 250** (was 160) |
| FAQ / answerability | **Words > 450** (was 320) |
| Citation | **Words > 320** and **citation index &lt; 28** (was 250 / 32) |
| JSON-LD missing | **Words > 400** (was 200) |
| Trust layer thin | **Words > 350** (was 200) |
| Image alt | **≥ 6** images and alt ratio **&lt; 0.30** (was 4 / 0.35) |
| Confidence | JSON-LD penalty only if **words > 450** (was 300) |

## Partial pipeline / Playwright

When limitations include `PARTIAL_PIPELINE`, `PLAYWRIGHT_FAILED`, or `PLAYWRIGHT_NO_GAIN`, cross-check scores manually. **Cal-02** adds gentle GEO dampening and confidence caps when `partial` is true (see below).

## Adjustments applied: ruleset/scoring **v1-cal02**

Version strings: `ruleset-v1-cal02`, `scoring-v1-cal02`.

**`pipeline_context`** (injected on live scans before persist; merged on `rescore` from `ScanFetchResult`):

- `partial` (bool), `is_probably_spa` (**bool**, normalized on pipeline + rescore), `primary_fetch_method` (string, e.g. `http_playwright_attempted`).

| Area | Change |
|------|--------|
| SPA internal links | If `is_probably_spa` and the thin-link condition would apply → **no** `INTERNAL_LINKS_THIN` issue/reco; `internal_links` subscore floor **58** |
| Playwright non concluant | If `primary_fetch_method == http_playwright_attempted` → modulate thin-link handling (floor **54** with `internal >= 1`, else mild cap **56** without issue when `internal == 0`) |
| Article `MULTIPLE_H1` | Severity **low**, fix **3**, heading score floor **82** (provisional) |
| Long page H2 | Article: nag only if **word_count > 620** (non-article stays **> 520**) |
| FAQ / answerability | Article: floor **620** words; non-article **450** (both **provisional**) |
| Citation weak | Article: skip `CITATION_SIGNALS_WEAK` when **words ≥ 550**, **list items ≥ 8**, **H2 ≥ 2** (provisional) |
| Partial + GEO | All GEO subscores **×0.96**; if `partial` and (**words < 400** or **SPA**) → **GEO ≤ 77** (provisional cap) |
| Partial + confidence | Extra **−0.05** if SPA; **ceiling 0.68** if `partial` and (**words < 400** or **SPA**) → **not** `high` |
| Recommendations | After dedupe, **merge** `REWRITE_HERO` + `CLARIFY_OFFER_POSITIONING` → **`ABOVE_FOLD_CLARITY`**; cap list at **6**; shared wording for `IMPROVE_HEADING_STRUCTURE` |
| Hero CTA rule | Align cal-01 doc: CTA nag only if hero **> 28** words without CTA (was **> 15**) |
| JSON-LD / images | Align **cal-01** doc: JSON-LD missing if **words > 400**; image alt if **≥ 6** images and alt ratio **< 0.30** |

## Adjustments applied: ruleset/scoring **v1-cal03**

Version strings: `ruleset-v1-cal03`, `scoring-v1-cal03`.

| Area | Change |
|------|--------|
| Docs / editorial-like | Heuristic from **URL path** (`/docs`, `/documentation`, `/blog`, …), **react.dev** home, **nextjs.org** `/` or `/docs`/`/learn`, or long structured **other/article/about** (≥400 words, ≥4 H2, ≥12 internal links). When true: **no** `HERO_TOO_SHALLOW`, `HERO_CTA_WEAK`, `OFFER_TYPE_UNCLEAR` (and thus no merged **`ABOVE_FOLD_CLARITY`** from those); base hero/offer subscores unchanged |
| `is_probably_spa` in exports | Pipeline + rescore always persist a **boolean** (`False` if unknown after merge) so API/offline calibration rows stay comparable |

## Next steps

1. Run **API mode** on the corpus after `playwright install chromium` and compare to **offline** rows for JS-heavy URLs.
2. Keep **two calibration runs** (before/after rule changes) in `calibration/out/` for diff review.
3. Tune **provisional** floors/caps (620/450 words, GEO 77, citation thresholds) using real `calibration/out/*.json` exports.
