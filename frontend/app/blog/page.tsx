import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Blog",
  description:
    "Short, product-led notes on SEO, GEO, and single-page readiness — aligned with how GeoScore analyzes one URL.",
};

const POSTS: { slug: string; title: string; date: string; lede: string }[] = [
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

export default function BlogIndexPage() {
  return (
    <main className="resultMain blogIndex">
      <header className="blogIndexHeader">
        <h1 className="resultTitle">Blog</h1>
        <p className="muted blogIndexLead">
          Practical framing for SEO and GEO — written to match what GeoScore actually measures on a single public URL.
          No keyword churn, no “AI visibility hacks.”
        </p>
      </header>
      <ul className="blogPostList">
        {POSTS.map((p) => (
          <li key={p.slug}>
            <article className="card block blogPostCard">
              <p className="blogPostMeta">
                <time dateTime={p.date}>{p.date}</time>
              </p>
              <h2 className="h2 blogPostTitle">
                <Link href={`/blog/${p.slug}`}>{p.title}</Link>
              </h2>
              <p className="muted small">{p.lede}</p>
              <p className="blogPostRead">
                <Link href={`/blog/${p.slug}`}>Read</Link>
              </p>
            </article>
          </li>
        ))}
      </ul>
      <p className="muted small blogIndexFooter">
        <Link href="/">Home</Link>
        {" · "}
        <Link href="/how-it-works">How scoring works</Link>
      </p>
    </main>
  );
}
