import type { Metadata } from "next";
import Link from "next/link";

import { BlogBreadcrumbJsonLd } from "@/components/BlogBreadcrumbJsonLd";
import { BlogPostingJsonLd } from "@/components/BlogPostingJsonLd";
import { blogPostMetadata } from "@/lib/blogMetadata";
import { getBlogPostMeta } from "@/lib/blogPosts";

const POST = getBlogPostMeta("honest-limits-utility-trust")!;
const DESCRIPTION =
  "GeoScore as a narrow URL checker: limitations next to the score are a product feature, not an apology — like the best converter sites.";

export const metadata: Metadata = blogPostMetadata(POST, DESCRIPTION);

export default function BlogHonestLimitsUtilityPage() {
  return (
    <>
      <BlogBreadcrumbJsonLd variant="post" post={POST} />
      <BlogPostingJsonLd post={POST} description={DESCRIPTION} />
      <article className="blogArticle">
      <nav className="resultNavCrumb muted" aria-label="Breadcrumb">
        <Link href="/blog">Blog</Link>
        <span aria-hidden="true"> · </span>
        <span className="blogCrumbCurrent">Honest limits</span>
      </nav>

      <header className="blogArticleHeader">
        <h1 className="resultTitle">Why honest limits make a utility tool more trustworthy</h1>
        <p className="blogByline muted small">
          <span>GeoScore team</span>
          <span aria-hidden="true"> · </span>
          <time dateTime="2026-04-22">22 April 2026</time>
        </p>
        <p className="muted blogDeck">
          People keep using small web utilities — PDF converters, screenshot tools, compressors — not because they look
          impressive, but because they <strong>do one job</strong> and don&apos;t pretend to do more. A single-URL SEO/GEO
          read works the same way: the score is only as honest as the capture, so{" "}
          <strong>limitations belong in the product</strong>, not hidden in a footnote.
        </p>
      </header>

      <section className="card block" aria-labelledby="blog-narrow">
        <h2 className="h2" id="blog-narrow">
          Narrow scope, visible boundaries
        </h2>
        <p className="muted">
          GeoScore is intentionally not a full-site crawler or rank tracker. When analysis is partial — blocked fetch,
          thin HTML, JS-heavy shell — the useful response is to say so clearly, reduce confidence, and point you at{" "}
          <Link href="/how-it-works">what the engine actually measured</Link>. That is how you avoid selling a false
          sense of certainty before a launch or a client review.
        </p>
      </section>

      <section className="card block" aria-labelledby="blog-trust">
        <h2 className="h2" id="blog-trust">
          Trust comes from clarity, not chrome
        </h2>
        <p className="muted">
          Fancy dashboards age quickly; clear limits don&apos;t. If you want the same positioning for your own product
          pages, pair a tight promise with{" "}
          <Link href="/blog/confidence-limitations-read-diagnostic">visible confidence and limitations</Link> — the
          pattern works for diagnostic tools and for marketing copy that has to survive scrutiny.
        </p>
      </section>

      <p className="muted small blogIndexFooter">
        <Link href="/blog">← Blog</Link>
        {" · "}
        <Link href="/">Home</Link>
      </p>
    </article>
    </>
  );
}
