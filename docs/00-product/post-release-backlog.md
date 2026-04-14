# Post-release backlog (deferred only)

**Purpose:** hygiene — capture what **this release intentionally does not ship**, so ideas do not creep back into scope. **Source of truth for product sequencing:** `docs/00-product/roadmap-v2-v3.md`. **Ops / platform deferrals:** `docs/03-build/release-readiness.md` P1 / P2. **Not listed here:** anything that would **broadly reopen** scoring (`scoring-v1-cal03` / `ruleset-v1-cal03` per `AGENTS.md`), or net-new product lines not named in the roadmap.

**Rule:** this file is **not** a commitment to build; prioritize only when you open a planning window.

---

## Later V2 (roadmap §B — after short V2: Projects + compare)

| Item | Why it matters | Why deferred | Priority after release |
|------|----------------|--------------|------------------------|
| **Lightweight multi-page (3–7 URLs)** | Key URLs checked together without tab sprawl; differentiator vs single-page toys | Needs batch/queue API, hard cap, honest cost/limit copy — extends ingestion beyond one artifact | **High** |
| **Rollup / “site snapshot” view** | See weakest page in a small set | Depends on multi-scan read model (typically after bundles exist); must stay aggregate-from-outputs only | **Medium** (after or with bundle MVP) |
| **Stronger recommendation / action layer** | Clearer next steps, checklists, export, “copy fix list” | Commercial polish once core repeat/compare workflows are proven in market | **Medium** |
| **Soft usage signals (no billing)** | Fewer surprise failures; honest “getting heavy” messaging | Optional roadmap row; no Stripe required — still needs product copy + counter design | **Low–medium** |

---

## V3 (roadmap §C — time, competition, workflow, apps)

| Item | Why it matters | Why deferred | Priority after release |
|------|----------------|--------------|------------------------|
| **Scheduled / recurring scans** | Drift after releases; “always-on readiness” narrative | Job runner, notifications, retention, abuse — roadmap pairs with quotas maturity | **High** (among V3) |
| **Competitor comparison (bounded)** | Benchmark comparable pages | Ethics, fairness, copy — roadmap: wait until **your** compare UX is default | **Medium** |
| **Rewrite assistance (bounded)** | Recos → draft edits | LLM budget, templates, review step — moves product toward workflow; trust cost | **Medium** |
| **App listing analysis + ASO + GEO** | Same readiness story for store listings | New extraction family; roadmap allows **targeted** score surfaces only — not blanket engine reopen | **Medium** |
| **Historical trends (many runs)** | “Trending up?” over time | Needs enough stored history + chart UX; roadmap: not a BI platform | **Low** |

*Roadmap §B “postpone” notes (competitor, schedules) align with this V3 bucket — not duplicated under Later V2.*

---

## Much later / optional (roadmap §C postpone + release-readiness P2 / non-product P1)

| Item | Why it matters | Why deferred | Priority after release |
|------|----------------|--------------|------------------------|
| **Enterprise: workspaces, SSO, complex RBAC** | Teams at scale | Violates minimal-analyzer positioning until product is proven; roadmap §C postpone | **Low** (unless strategy shifts) |
| **Billing / Stripe, usage tiers** | Sustainable revenue | Roadmap: not prerequisite for sequencing; readiness P2 — keep diagnostic value first | **Medium** (business-driven) |
| **Magic-link email, password accounts** | Stronger auth UX | Readiness P2; MVP email session sufficient for first releases | **Medium** |
| **Full observability (APM, dashboards)** | Ops at scale | Readiness P2; cost/complexity | **Low** |
| **Multi-region, replicas, advanced cache** | Scale | Readiness P2; premature before traffic | **Low** |
| **CI: integration job (Postgres + smoke script)** | Catch wiring regressions | Readiness P1 optional — slower CI; ship value first | **Medium** (engineering) |
| **Rate limits / abuse (auth + scans)** | Abuse resistance | Readiness P1; when traffic warrants | **Medium** (engineering) |
| **Structured logging + request id** | Incident triage | Readiness P1; when on-call pain appears | **Medium** (engineering) |
| **Security headers (CSP, HSTS)** | Hardening | Readiness P1; often at reverse proxy | **Low–medium** (engineering) |

---

## Explicitly out of this backlog (constraints, not tickets)

- **Broad scoring / ruleset recalibration** — frozen per `AGENTS.md`; only exceptional **targeted** fixes with explicit rationale, not backlog “features.”
- **Full-site black-box “site score”** — roadmap prefers transparent rollups from page outputs; do not add as a shortcut.
- **Unbounded crawl / sitemap discovery** — excluded from V2 multi-page scope in roadmap.

---

*Update when `roadmap-v2-v3.md` is revised. Do not use this file to justify scope during an active release freeze.*
