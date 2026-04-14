# GeoScore — feature prioritization matrix

**Purpose:** decision-oriented view of **where** each candidate belongs (short V2 / later V2 / V3 / much later).  
**Authority:** `roadmap-v2-v3.md` + `AGENTS.md` (scoring frozen); `release-readiness.md` (billing not P0); `positioning.md` (minimal analyzer, not enterprise suite).  
**Effort / risk scale:** **L** = low, **M** = medium, **H** = high (relative to current codebase: single-URL scan + dashboard + auth).

---

## Prioritization table

| # | Feature | Product value | Impl. effort | Tech risk | Product / scope risk | Dependency / prerequisite | Timing | One-line reason |
|---|---------|---------------|--------------|-----------|----------------------|-----------------------------|--------|-----------------|
| 1 | **Projects** | Repeatable, client/site grouping; invoice-friendly history | **L** | **L** | **L** (if capped: no teams) | DB `projects` + scan `project_id`; auth | **short V2** | Smallest structural win vs “pile of UUIDs”; already aligned with disciplined roadmap #1. |
| 2 | **Compare to previous run** | Before/after narrative on **your** URL; trust via stored payloads | **L** | **L** | **L** (if presentation-only diff) | `parent_scan_id` / rescan; two detail payloads | **short V2** | High clarity per line of code; proves iteration story without new scoring engine. |
| 3 | **Multi-page bundle (3–7 URLs)** | Bounded “snapshot” of a small set of key pages | **M** | **M** | **M** (cost, UX, cap enforcement) | Queue/batch API; hard cap + honest copy; cost per scan still bounded | **later V2** | Real differentiator but extends ingestion beyond one URL → ship after projects+compare prove workflow. |
| 4 | **Rollup / site snapshot** | “Weakest page” / min-max table across a bundle | **M** | **L–M** | **M** (must stay aggregate-from-outputs, not new black-box) | Multi-scan read model (bundle or manual set); **no** second scoring engine | **later V2** | Value follows bundles; aggregation-only keeps positioning honest. |
| 5 | **Stronger recommendation / action layer** | Clearer next steps, checklists, export, “copy fix list” | **L–M** | **L** | **L–M** (avoid CMS integration creep) | Existing issues/recos API shape; mostly UX + export | **later V2** | Commercial polish without reopening scoring; low infra vs schedules/competitors. |
| 6 | **Soft usage limits / signals (no billing)** | Fewer surprise failures; honest “getting heavy” messaging | **L** | **L** | **L** | Counters or lightweight rate hints; **no** Stripe as gate | **later V2** | Improves trust before monetization narrative; roadmap optional #6. |
| 7 | **Scheduled scans** | Drift detection over time; “always-on” story | **H** | **H** | **H** (abuse, retention, notifications) | Job runner, email/push, quotas policy | **V3** | Roadmap explicitly V3; pairs with abuse/ops work you should not take before compare is proven. |
| 8 | **Competitor comparison** | Benchmark vs third-party page | **M–H** | **M** | **H** (fairness, positioning, debate) | Mature compare UX on own pages; ethics/copy for “observable snapshot only” | **V3** | Roadmap: wait until **your** before/after story is default; third-party opens trust + scope. |
| 9 | **Rewrite assistance** | Turn recos into bounded draft edits | **M–H** | **M** | **H** (LLM cost, quality, liability) | LLM budget caps, user review step, `llm-strategy` discipline | **V3** | Moves product toward “workflow”; needs bounded assist model, not V2 core diagnostic. |
| 10 | **App listing / ASO analysis** | Same readiness story for store listings | **H** | **H** | **H** (new extraction family; may tempt ruleset expansion) | New surfaces; **targeted** rules only if ever — not blanket recalibration | **V3** | Roadmap V3 #4; new category, not “minimal web page analyzer” extension. |
| 11 | **Trends / time-based history** | “Are we trending up?” across many runs | **M** | **M** | **M** (chart UX ≠ BI platform) | Enough stored runs per URL/project; retention policy | **V3** | Roadmap V3 #5; meaningful after users accumulate scans (post scheduling optional). |
| 12 | **Billing / plans** | Revenue, tiers, sustainable ops | **M** (Stripe exists in stack) | **M** | **H** if made **center** of roadmap | Legal/pricing, support load, gating UX | **much later / not now** *(product sequencing)* | `release-readiness.md` P2; roadmap says billing **not** prerequisite — ship value first, monetize when discipline requires. |
| 13 | **Enterprise / workspaces / RBAC** | Teams, SSO, admin | **H** | **H** | **H** (violates minimal positioning) | Multi-tenant model, security review, sales motion | **much later / not now** | `positioning.md` + roadmap postpone; turns GeoScore into suite you explicitly avoid. |
| 14 | **Broad scoring recalibration** | “Refresh” model feel industry-wide | **H** (touch core) | **H** | **H** (breaks explainability promises mid-flight) | New calibration process, migration narrative | **much later / not now** *(frozen)* | **Forbidden as roadmap item:** `AGENTS.md` — only **targeted** fixes when a case is clearly wrong; no broad reopen. |

---

## A. Top 2 features for the best short V2

1. **Projects** — smallest repeatability / grouping win.  
2. **Compare to previous run** — iteration story with **presentation-only** diff on existing payloads.

---

## B. Top 3 features for later V2

1. **Multi-page bundle (3–7 URLs)** — bounded breadth; requires batch/queue + cap discipline.  
2. **Rollup / site snapshot** — aggregate **from scan outputs** after bundles exist.  
3. **Stronger recommendation / action layer** OR **soft usage signals** — pick one first by operator pain; both stay **non-billing**, **non-scoring**.

*(If forced to rank the last slot: **stronger rec/action layer** slightly edges **soft signals** for commercial clarity without infra.)*

---

## C. Top 3 features for V3

1. **Scheduled scans** — time dimension + jobs; after on-demand workflow is trusted.  
2. **Competitor comparison (bounded)** — after own-page compare is mature and copy is tight.  
3. **Rewrite assistance (bounded)** — workflow assist under strict LLM/cost/review constraints.

*(**App listing / ASO** and **trends** follow closely in V3 ordering per `roadmap-v2-v3.md`.)*

---

## D. Features that should explicitly stay frozen for now

| Item | Rule |
|------|------|
| **Broad scoring recalibration** | No `ruleset-v1-cal03` / `scoring-v1-cal03` reopen for “vibes”; targeted fixes only per `AGENTS.md`. |
| **Enterprise / workspaces / RBAC** | Not on the path until product is definitively not “minimal analyzer.” |
| **Billing as the sequencing driver** | Do not reorder roadmap around Stripe; billing when revenue ops need it, not to unlock core V2. |

---

## E. Final recommendation

| Lens | Guidance |
|------|------------|
| **What to build next** | Finish and ship **short V2 = Projects + Compare**; then **bounded multi-page bundle** as first **later V2** expansion if traction warrants breadth. |
| **What to avoid touching** | **Deterministic scoring core** (broad recalibration), **enterprise auth surface**, **competitor / schedule / rewrite** until V3 is consciously opened. |
| **Most value / least risk** | **Projects + Compare**: uses existing DB fields and stored payloads, reinforces positioning (“before/after”, “shareable diagnostic”), and does **not** expand crawl surface, LLM workflow, or billing complexity. |

---

*When `vision.md` §V2 conflicts with this matrix, prefer **`roadmap-v2-v3.md`** for sequencing. Update this file when a release train commits scope.*
