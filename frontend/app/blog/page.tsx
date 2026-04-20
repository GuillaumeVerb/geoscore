import type { Metadata } from "next";
import Link from "next/link";

import { BLOG_POSTS } from "@/lib/blogPosts";

export const metadata: Metadata = {
  title: "Blog",
  description:
    "Short, product-led notes on SEO, GEO, and single-page readiness — aligned with how GeoScore analyzes one URL.",
};

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
        {BLOG_POSTS.map((p) => (
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
