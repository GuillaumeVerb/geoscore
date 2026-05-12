import type { Metadata } from "next";
import Link from "next/link";

import { BlogBreadcrumbJsonLd } from "@/components/BlogBreadcrumbJsonLd";
import { BlogPostingJsonLd } from "@/components/BlogPostingJsonLd";
import { blogPostMetadata } from "@/lib/blogMetadata";
import { getBlogPostMeta } from "@/lib/blogPosts";

const POST = getBlogPostMeta("documentation-pages-structure-findability-trust")!;
const DESCRIPTION =
  "One docs URL: outline-style structure, findability, and trust signals — bridging classic SEO and GEO without pretending to index your whole knowledge base.";

export const metadata: Metadata = blogPostMetadata(POST, DESCRIPTION);

export default function BlogDocumentationPagesPage() {
  return (
    <>
      <BlogBreadcrumbJsonLd variant="post" post={POST} />
      <BlogPostingJsonLd post={POST} description={DESCRIPTION} />
      <article className="blogArticle">
        <nav className="resultNavCrumb muted" aria-label="Breadcrumb">
          <Link href="/blog">Blog</Link>
          <span aria-hidden="true"> · </span>
          <span className="blogCrumbCurrent">Documentation pages</span>
        </nav>

        <header className="blogArticleHeader">
          <h1 className="resultTitle">Documentation pages: structure, findability, and trust</h1>
          <p className="blogByline muted small">
            <span>GeoScore team</span>
            <span aria-hidden="true"> · </span>
            <time dateTime="2026-04-23">23 April 2026</time>
          </p>
          <p className="muted blogDeck">
            A documentation URL is often the <strong>second moment of truth</strong> after the homepage: the reader
            already believes you might solve their problem and needs proof they can <strong>execute</strong> without
            filing a ticket. This note stays on <strong>one public page</strong> — the same snapshot mindset as GeoScore.
          </p>
        </header>

        <section className="card block" aria-labelledby="blog-structure">
          <h2 className="h2" id="blog-structure">
            Structure: make the page scannable before it is beautiful
          </h2>
          <p className="muted">
            Strong docs read like an outline: a single H1, logical H2/H3 progression, and paragraphs short enough that a
            busy developer can jump to the right section. Long walls of prose fail twice — in search snippets and when
            someone tries to extract “the three steps” into a note or an answer engine. Prefer explicit prerequisites,
            numbered procedures, and code or config blocks labeled with language and context so they survive copy-paste
            and summarization.
          </p>
        </section>

        <section className="card block" aria-labelledby="blog-findability">
          <h2 className="h2" id="blog-findability">
            Findability: titles and paths that match real queries
          </h2>
          <p className="muted">
            Page titles and headings should match the words people type when stuck (“Install”, “Migrate”, “Webhook
            retries”), not internal codenames only your team uses. Cross-link related pages in-line where the reader’s
            next question appears — not only in a generic “See also” footer. If your docs product offers search, this
            public URL still benefits from self-contained clarity: the first screen should say what the page covers so
            deep links from Google or chat UIs land gracefully.
          </p>
        </section>

        <section className="card block" aria-labelledby="blog-trust">
          <h2 className="h2" id="blog-trust">
            Trust: versioning, limits, and honesty under pressure
          </h2>
          <p className="muted">
            Readers forgive ugly CSS faster than they forgive ambiguous security claims or silent breaking changes. When
            behavior differs by plan or region, say so near the procedure. When something is beta or deprecated, label it
            visibly. Dates or version banners are not vanity — they signal that the page is maintained. That overlaps with
            GEO-style <strong>citation readiness</strong> (accurate extraction without invented caveats); see{" "}
            <Link href="/blog/citation-ready-real-marketing-page">citation-ready on a marketing page</Link> for the same
            idea on a different page type.
          </p>
        </section>

        <section className="card block" aria-labelledby="blog-seo-geo">
          <h2 className="h2" id="blog-seo-geo">
            SEO and GEO on the same URL
          </h2>
          <p className="muted">
            Classic SEO still cares about titles, meta where present, and crawlable structure. GEO-style readiness adds:
            can someone state what this page teaches in one sentence? GeoScore keeps those lenses <strong>separate
            scores</strong> on one snapshot so you can see technical hygiene and extractability diverge — the frame in{" "}
            <Link href="/blog/seo-vs-geo-one-page">SEO vs GEO on one page</Link>.
          </p>
        </section>

        <section className="card block" aria-labelledby="blog-scope">
          <h2 className="h2" id="blog-scope">
            What one URL cannot audit
          </h2>
          <p className="muted">
            A single docs page scan does not replace information architecture reviews, full-site search quality, or
            support analytics. It reflects <strong>that URL at that moment</strong>; when capture is partial, read{" "}
            <strong>confidence</strong> and <strong>limitations</strong> before you ship conclusions — as in{" "}
            <Link href="/blog/confidence-limitations-read-diagnostic">how to read a diagnostic honestly</Link>.
          </p>
        </section>

        <section className="card block" aria-labelledby="blog-measure">
          <h2 className="h2" id="blog-measure">
            Measure the page you ship
          </h2>
          <p className="muted">
            Paste the live documentation URL into GeoScore for structured <strong>SEO</strong> and <strong>GEO</strong>{" "}
            scores, issues, and fixes grounded in observable signals — see{" "}
            <Link href="/how-it-works">how scoring works</Link>. Sample layout:{" "}
            <Link href="/report/demo-example">example report</Link>.
          </p>
        </section>

        <p className="blogCta muted">
          <Link href="/#analyze" className="button">
            Analyze a docs URL
          </Link>
          {" · "}
          <Link href="/how-it-works">How scoring works</Link>
          {" · "}
          <Link href="/blog">All posts</Link>
        </p>
      </article>
    </>
  );
}
