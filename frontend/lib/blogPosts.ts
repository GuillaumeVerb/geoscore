/** Blog index + sitemap — keep slugs in sync with `app/blog/<slug>/`. */
export type BlogPostMeta = { slug: string; title: string; date: string; lede: string };

export const BLOG_POSTS: BlogPostMeta[] = [
  {
    slug: "honest-limits-utility-trust",
    title: "Why honest limits make a utility tool more trustworthy",
    date: "2026-04-22",
    lede:
      "The same reason people trust a plain PDF converter: the job is narrow, the output is clear, and the product admits what it could not see.",
  },
  {
    slug: "pricing-pages-clarity-beats-keyword-stuffing",
    title: "Pricing pages: clarity beats keyword stuffing",
    date: "2026-04-21",
    lede:
      "One pricing URL: who it is for, what they get, what it costs — structured for buyers and for fair extraction, not for SEO theater.",
  },
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

export function getBlogPostMeta(slug: string): BlogPostMeta | undefined {
  return BLOG_POSTS.find((p) => p.slug === slug);
}
