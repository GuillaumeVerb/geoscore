import type { Metadata } from "next";
import Link from "next/link";

import { BlogPostingJsonLd } from "@/components/BlogPostingJsonLd";
import { blogPostMetadata } from "@/lib/blogMetadata";
import { getBlogPostMeta } from "@/lib/blogPosts";

const POST = getBlogPostMeta("homepage-readiness-bounded-checklist")!;
const DESCRIPTION =
  "A fast, honest homepage pass you can do on one URL: structure, clarity, and trust signals — without pretending to audit an entire site.";

export const metadata: Metadata = blogPostMetadata(POST, DESCRIPTION);

export default function BlogHomepageReadinessPage() {
  return (
    <>
      <BlogPostingJsonLd post={POST} description={DESCRIPTION} />
      <article className="blogArticle">
      <nav className="resultNavCrumb muted" aria-label="Breadcrumb">
        <Link href="/blog">Blog</Link>
        <span aria-hidden="true"> · </span>
        <span className="blogCrumbCurrent">Homepage readiness</span>
      </nav>

      <header className="blogArticleHeader">
        <h1 className="resultTitle">Homepage readiness: a bounded checklist (no enterprise crawl)</h1>
        <p className="blogByline muted small">
          <span>GeoScore team</span>
          <span aria-hidden="true"> · </span>
          <time dateTime="2026-04-20">20 April 2026</time>
        </p>
        <p className="muted blogDeck">
          Your homepage is the default face of the product. This post is a <strong>bounded</strong> pass: one URL, one
          snapshot mindset — the same scope GeoScore uses. It is not a substitute for a full-site crawl or a rank
          tracker; it is what you can sanity-check before launch or after a big hero change.
        </p>
      </header>

      <section className="card block" aria-labelledby="blog-why">
        <h2 className="h2" id="blog-why">
          Why “one homepage URL” is enough to start
        </h2>
        <p className="muted">
          Most serious problems on a homepage show up in the <strong>rendered page</strong>: unclear value proposition,
          weak structure, missing or generic meta, buried proof, or copy that does not survive being summarized. You do
          not need a hundred-tab suite to ask: “Would a human or a retrieval system understand what we sell in under a
          minute?” A single-URL analyzer is honest about that scope — and should surface{" "}
          <strong>limitations</strong> when the capture is partial instead of inventing certainty.
        </p>
      </section>

      <section className="card block" aria-labelledby="blog-checklist">
        <h2 className="h2" id="blog-checklist">
          The checklist (keep it under 30 minutes)
        </h2>
        <ul className="hiwList muted">
          <li>
            <strong>Above the fold:</strong> Can a stranger name what you sell and who it is for — without scrolling?
          </li>
          <li>
            <strong>Headline + subhead:</strong> One primary claim, one supporting line; avoid stacked vague superlatives.
          </li>
          <li>
            <strong>Primary action:</strong> One obvious next step (sign up, book, try). Secondary links do not compete
            for attention.
          </li>
          <li>
            <strong>Proof near the claim:</strong> Logos, metrics, or quotes close to the promise — not only in a
            footer wall.
          </li>
          <li>
            <strong>Headings as outline:</strong> H1 once; following headings read like a coherent table of contents.
          </li>
          <li>
            <strong>Technical basics visible:</strong> Title and meta description present and human-readable; no obvious
            broken layout on mobile width.
          </li>
          <li>
            <strong>Internal paths:</strong> Pricing, docs, or product areas reachable in one or two obvious clicks —
            not a maze.
          </li>
          <li>
            <strong>Trust without noise:</strong> Security, privacy, or compliance cues where your audience expects
            them — especially for B2B.
          </li>
        </ul>
      </section>

      <section className="card block" aria-labelledby="blog-skip">
        <h2 className="h2" id="blog-skip">
          What this checklist deliberately skips
        </h2>
        <p className="muted">
          Full backlink graphs, position tracking, competitor sets, and crawl-everything audits belong to different
          tools — and often to different phases of the work. GeoScore is intentionally a <strong>minimal analyzer</strong>{" "}
          (<Link href="/pricing">see how we think about scope</Link>): one URL in, structured scores and fixes out. If
          you need site-wide coverage, plan that separately; do not pretend a homepage pass replaced it.
        </p>
      </section>

      <section className="card block" aria-labelledby="blog-tool">
        <h2 className="h2" id="blog-tool">
          Turn the checklist into a measured read
        </h2>
        <p className="muted">
          When you want the same dimensions expressed as <strong>SEO and GEO scores</strong>, issues, and prioritized
          fixes on the live page, run GeoScore on the URL and read the result alongside{" "}
          <Link href="/how-it-works">how scoring works</Link>. Rescan after you ship changes if you want a before/after
          story on the same page (see dashboard and compare when a parent scan exists).
        </p>
      </section>

      <p className="blogCta muted">
        <Link href="/#analyze" className="button">
          Analyze your homepage
        </Link>
        {" · "}
        <Link href="/blog/seo-vs-geo-one-page">SEO vs GEO on one page</Link>
        {" · "}
        <Link href="/blog">All posts</Link>
      </p>
    </article>
    </>
  );
}
