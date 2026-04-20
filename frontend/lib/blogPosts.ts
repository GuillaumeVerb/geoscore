/** Blog index + sitemap — keep slugs in sync with `app/blog/<slug>/`. */
export type BlogPostMeta = { slug: string; title: string; date: string; lede: string };

export const BLOG_POSTS: BlogPostMeta[] = [
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
