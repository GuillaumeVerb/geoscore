/** Blog index + sitemap — keep slugs in sync with `app/blog/<slug>/`. */
export type BlogPostMeta = { slug: string; title: string; date: string; lede: string };

export const BLOG_POSTS: BlogPostMeta[] = [
  {
    slug: "citation-ready-real-marketing-page",
    title: "What “citation-ready” means on a real marketing page",
    date: "2026-04-20",
    lede:
      "Clear intent, extractable structure, and on-page trust — without promising AI citations or collapsing GEO into hype.",
  },
  {
    slug: "confidence-limitations-read-diagnostic",
    title: "Confidence and limitations: how to read a diagnostic honestly",
    date: "2026-04-20",
    lede:
      "When to trust the headline scores, how partial scans show up, and why limitations next to the result are a feature — not an embarrassment.",
  },
  {
    slug: "homepage-readiness-bounded-checklist",
    title: "Homepage readiness: a bounded checklist (no enterprise crawl)",
    date: "2026-04-20",
    lede:
      "A fast pass on one URL — structure, clarity, proof — without pretending a homepage check replaced a full-site audit.",
  },
  {
    slug: "seo-vs-geo-one-page",
    title: "SEO vs GEO: what actually changes for one page",
    date: "2026-04-09",
    lede:
      "Two lenses on the same snapshot: classic search readiness vs how well the page can be understood, summarized, and cited.",
  },
];
