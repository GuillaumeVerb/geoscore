# GeoScore — release candidate notes (draft)

**Audience:** internal summary + user-facing changelog draft. **Scoring:** frozen at `scoring-v1-cal03` / `ruleset-v1-cal03`. **Positioning:** lightweight SEO & GEO analyzer — not a full SEO suite (see `docs/00-product/positioning.md`).

---

## 1. Internal release summary

This RC bundles **stable V1.5 core** (single public URL → structured SEO + GEO diagnostic, explainable scores, issues, recommendations, confidence, limitations, partial/failed handling, page-type override, rescan, shareable public report, dashboard, minimal email-based session auth, CI, `/ready`, Alembic migrations) with the **short V2 slice** already scoped in `docs/00-product/roadmap-v2-v3.md`: **Projects** (grouping + dashboard filter + optional assignment at scan creation) and **Compare to previous run** (presentation-only before/after for rescan lineage via `parent_scan_id`). No scoring calibration reopen, no billing ship, no multi-page bundle in this train. Operators should run `docs/03-build/verify-deployment.md` (including Short V2 smoke) and `docs/03-build/release-candidate-checklist.md` before tag.

---

## 2. User-facing changelog (draft)

**GeoScore — release candidate**

- **Projects** — Organize scans with simple named projects. Filter your dashboard history by project, and attach new analyses to a project when you start them from the dashboard.
- **Compare runs** — After you **rescan** a page, open a **before / after** view: scores (Global, SEO, GEO), issues that cleared or appeared, and how recommendations shifted. Differences are shown from **each run’s saved results** (not a separate “AI rerank” of your site).
- **Reliability & clarity** — Session and error copy tightened in places; deploy/runbook guidance improved for split frontend + API setups (CORS, HTTPS, env).
- **Unchanged by design** — Still one primary flow: paste a URL, get one serious result. Auth remains email + session token (no magic link inbox yet). **Billing is not live** (see Pricing page). Scoring engine and ruleset versions stay on the current frozen calibration unless a future release explicitly documents a targeted fix.

---

## 3. What’s included now

- Single-page **SEO + GEO** analysis with **Global / SEO / GEO** scores, strengths, issues, prioritized recommendations, limitations, and confidence.
- **Page type** detection with **user override** where supported.
- **Rescan** from a completed run; **public share** of a read-only report link.
- **Dashboard** of your scans (private to your session).
- **Projects:** create/list projects; filter history; optional project on new scan from dashboard.
- **Compare to previous run** for the **newer scan in a rescan pair** (dashboard + result entry points when applicable).
- **How scoring works** in-product; **example demo report** for prospects without an account.
- **Health + readiness** endpoints for operators; **migrations** path documented for Postgres.

---

## 4. What is intentionally not included yet

- **Billing / paid plans / Stripe checkout** — not part of this RC; Pricing describes direction only.
- **Magic-link email, passwords, SSO, teams / workspaces / RBAC.**
- **Multi-page bundles**, **site-wide rollups**, **competitor comparison**, **scheduled scans**, **rewrite assistance**, **app store / ASO** — tracked as later phases in the product roadmap, not shipped here.
- **Broad rescoring or ruleset recalibration** — scoring stays on the frozen calibration; changes would be exceptional and called out explicitly in a future release, not bundled silently in this one.

---

## 5. What comes next (no dates, no promises)

Follow-up work stays **disciplined** in `docs/00-product/roadmap-v2-v3.md`: likely next product increments are **bounded breadth** (e.g. small multi-URL snapshot) and **UX polish** around recommendations and usage clarity — only when there is clear demand and capacity. **Operational** improvements (rate limits, integration smoke in CI, tighter logging) may land independently of product marketing. Nothing above is a commitment to ship or to prioritize; the RC stands on **repeatable single-URL diagnostics + projects + rescan compare** alone.

---

*Draft — adjust version label and date when tagging. Remove or archive after publishing an official changelog if you maintain one elsewhere.*
