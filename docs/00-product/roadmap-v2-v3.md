# GeoScore — roadmap V2 / V3 (disciplined)

**Context:** V1.5 is release-ready core (single URL, SEO+GEO, issues/recos, confidence/limitations, partial/failed, public report, dashboard, minimal auth, deploy, Alembic, in-product method). **Scoring engine stays frozen** except targeted fixes (`AGENTS.md`). **Billing is not a prerequisite** for sequencing below.

This doc refines `vision.md` bullets into **shippable phases** without scope creep.

---

## A. Current product baseline (V1.5)

### What already covers the promise well

- One serious **page-level** diagnostic (fetch/render → extract → score → explain).
- **GEO + SEO** visible, not bolted on as an afterthought.
- **Explainability:** issues, recs, limitations, confidence, page type override, `/how-it-works`.
- **Shareability:** public report; **continuity:** dashboard + auth scoping.
- **Ops credibility:** CI, `/ready`, migrations — product is defensible in market.

### What should stay frozen for now (do not “reopen” casually)

- **Calibration / ruleset** broad recalibration (`scoring-v1-cal03` / `ruleset-v1-cal03`).
- **Core pipeline shape:** one URL → one scan artifact (until V2 explicitly extends ingestion).
- **Positioning:** minimal analyzer — not an enterprise SEO suite.

---

## B. V2 roadmap — “Stronger for teams that ship pages”

### Vision

GeoScore becomes the **default check** before and after you change important URLs: still **fast and explainable**, but **multi-page aware** and **comparison-native** — without becoming a rank tracker or full crawler.

### Top goals

1. **Repeatability:** same user sees related scans grouped and comparable.
2. **Iteration:** before/after is a first-class story (not “find two scan IDs manually”).
3. **Breadth (bounded):** a **small bundle of URLs** per project — not unbounded site crawls.

### Features (recommended order)

| Priority | Feature | User problem solved | Prerequisites | Exclude / scope cap |
|----------|---------|----------------------|---------------|---------------------|
| **1** | **Projects (domain / client grouping)** | “My scans are a pile of UUIDs; I work per site or per client.” | DB already has `projects`; wire UX + default project optional | No workspaces/teams/RBAC |
| **2** | **Before / after compare (2 scans)** | “Did my launch change move the needle?” | `parent_scan_id` / rescan exists; need UI + diff view on **existing** score/issue payloads | No new composite “delta score” formula in engine — **presentation diff** first |
| **3** | **Lightweight multi-page (3–7 URLs)** | “Home + pricing + docs matter together; I don’t want three tabs.” | Queue/batch API, **hard cap** per run, clear cost/limit copy | Not full-site crawl; not sitemap discovery in V2 |
| **4** | **Rollup / “site snapshot” view** | “What’s the weakest page in this bundle?” | Multi-scan read model; **min/avg table** or “worst issues” aggregation | Not a second scoring engine — aggregate **from scan outputs** |
| **5** | **Recommendation layer polish** | “I know what’s wrong; I need a clearer next step.” | UX: checklists, export, “copy fix list”, optional print-friendly public report | Not full CMS integration |
| **6** (optional) | **Usage signals without billing** | “I’m hitting limits unexpectedly.” | Soft counters, honest messaging | No Stripe dependency for V2 core |

### What to postpone (still “V2-ish” but later or V3)

- **Competitor URL compare** (third-party pages + fairness + more debate) — high product surface, wait until compare UX is proven on **your** pages.
- **Scheduled scans** — cron + email + abuse — pairs naturally with billing/quotas; **V3** unless you accept a tiny internal cron MVP.

---

## C. V3 roadmap — “Ambitious expansion, new surfaces”

### Vision

GeoScore stretches to **time** (scheduling), **competition**, **rewrites**, and **apps** — still bounded and explainable, but clearly **beyond single-page marketing**.

### Top goals

1. **Proactive:** monitoring over time, not only on-demand.
2. **Creative assist:** rewrite help **bounded** by LLM strategy — not auto-publishing junk.
3. **New markets:** store listings / ASO + GEO.

### Features (recommended order)

| Priority | Feature | User problem solved | Prerequisites | Exclude |
|----------|---------|----------------------|---------------|---------|
| **1** | **Scheduled / recurring scans** | “Track drift after releases.” | Job runner, notifications, retention policy | Not “enterprise scheduler” day one |
| **2** | **Competitor comparison (bounded)** | “How do we stack up on comparable pages?” | V2 compare UX mature; ethics/copy for “observable snapshot only” | Not rank guarantees |
| **3** | **Rewrite assistance (bounded)** | “Turn recos into draft edits.” | LLM budget, templates, user review step | Not replacing human judgment; not auto-deploy |
| **4** | **App listing analysis + ASO + GEO** | “Same readiness story for the store.” | New extraction family, new score **surfaces** (may need **targeted** rulesets — not a blanket engine reopen) | Not full ASO suite (keywords, reviews mining) in v1 of V3 |
| **5** | **Historical trends (many runs)** | “Are we trending up?” | Storage, charts, anomaly hints | Not BI platform |

### What to postpone

- Multi-tenant enterprise admin, SSO, complex RBAC.
- Full **site-level** recalibrated scoring as a **new black-box** — prefer transparent rollups from page scans.

---

## D. Recommended build order (engineering + product)

1. **Projects (grouping + dashboard filter)** — smallest strong step; unlocks agency narrative.  
2. **Compare two scans (same user / same project)** — high “wow” per line of code if diff is presentation-only.  
3. **Bounded multi-URL bundle** — cap + queue + one “snapshot” result page.  
4. **Rollup / weakest-page summary** — aggregate UI only first.  
5. **Recos export / checklist UX** — commercial polish without new scoring.  
6. *(Optional)* soft usage limits messaging.  
→ **Then V3:** schedules → competitor → rewrite assist → app/ASO.

**Smallest “short V2” that is still strong:** **(1) Projects + (2) Compare**. Everything else is optional until traction.

---

## E. Commercial / product lens

### V2 features that strengthen GeoScore soon after launch

- **Projects + compare** — matches positioning (“share with client/cofounder”, “before/after”) with **clear invoice-friendly story**.
- **Bounded multi-page snapshot** — differentiates from single-page toys **without** claiming full SEO suite.

### V3 features that are most differentiating (longer arc)

- **Scheduled scans** — “always-on readiness” narrative.
- **App listing + ASO+GEO** — new category expansion.
- **Bounded rewrite assist** — moves from diagnostic to **workflow** (careful positioning).

---

## Final recommendation (summary)

| Question | Answer |
|----------|--------|
| **Best “short V2”** | **Projects + before/after compare** (presentation-layer diff; no new calibration). |
| **Definitely wait for V3** | **Scheduled scans**, **competitor compare**, **rewrite assist**, **app/ASO** — each opens infra, trust, or scope that V2 should prove first. |
| **Do not touch for now** | **Broad scoring engine / ruleset recalibration**; **enterprise complexity**; **billing as a gate** to the first V2 slice. |

---

*Aligned with `vision.md`, `positioning.md`, `product-strengthening-plan.md`, and `AGENTS.md`. Update this file when V2 scope is committed for a release train.*
