# Product strengthening (pre-release)

**Goal:** stronger perceived quality, credibility, and clarity at launch — without feature sprawl, billing, major scoring changes, or infra depth. Scoring stays frozen at **`scoring-v1-cal03` / `ruleset-v1-cal03`** (see `AGENTS.md`).

---

## 1. Audit (release-quality lens)

| Area | Observation |
|------|----------------|
| **Score & method** | Scores are visible; the *why* (rules-first, GEO + SEO) was mostly in marketing docs, not in-product. |
| **Credibility** | Positioning is strong in `positioning.md`; the live app needed a short, sober **“how it works”** path for skeptical visitors. |
| **Help / clarity** | No dedicated in-app explanation of limitations, confidence, or deterministic vs opaque tools. |
| **Demo** | `/report/demo-example` works; framing could stress “same structure as production” and method transparency. |
| **Issues / recos** | Wording comes from the pipeline; product pass = **UI framing** (section intros, confidence) rather than rewriting rules. |
| **Critical UX** | Landing + result + sign-in are fine; gaps were **cross-links** and **method transparency** on the result surface. |

---

## 2. Priority groups

### Must-do before a “very good” first release

- In-app **method & credibility** page (`/how-it-works`) aligned with vision + positioning (deterministic first, explainable, not a black box).
- **Nav + landing** discovery of that page (one click from global nav; optional link from hero).
- On **scan result** (and shared public report where relevant): a **short “how scoring works”** line + deep link, and version labels when `meta` exposes them.

### Strong upgrades if small (done or easy follow-ups)

- Tighter **example report** framing copy (demo vs live, no hype).
- **Sign-in** one-liner on privacy / same-email history (trust).
- Optional: **FAQ** accordion on `/how-it-works` after launch feedback.

### Can wait until after release

- Billing, usage UI, email magic links.
- Rewriting issue/reco catalog copy in the engine (would touch scoring/product pipeline).
- Video walkthrough, blog (see **`blog-strategy.md`** for a disciplined, product-led framing), comparison pages.
- Heavy onboarding tours.

---

## 3. Recommended order (product work)

1. **`/how-it-works`** (single source of truth for “what is this?”).  
2. **Global nav + landing** pointer.  
3. **`ScoreMethodNote`** on result + public report + demo layout consistency.  
4. **Copy passes**: sign-in, example framing.  
5. Post-launch: FAQ, analytics on where users drop off.

---

## 4. What shipped in-repo (this pass)

- `docs/00-product/product-strengthening-plan.md` (this file).
- `frontend/app/how-it-works/page.tsx` — concise method page.
- `frontend/lib/productCopy.ts` — frozen version strings for UI copy.
- `frontend/components/ScoreMethodNote.tsx` — result/public score footnote + link.
- `frontend/app/layout.tsx`, `LandingHero.tsx`, `ResultShell.tsx`, `PublicReportView.tsx`, `ExampleDemoPublicReportLayout.tsx`, `app/sign-in/page.tsx`, `globals.css` — wiring and small copy/CSS.

---

## 5. Still for a “very good” first release (non-code)

- Run **real URLs** (homepage, pricing, blog) and fix any **egregious** issue titles only if they mislead (targeted copy in pipeline layer — later).
- **Screenshot / social** card for launch (marketing, not code).
- Collect **3 testimonials** or “used by” strip (post-launch OK).
