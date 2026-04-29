import type { Metadata } from "next";
import Link from "next/link";

import { BlogPostingJsonLd } from "@/components/BlogPostingJsonLd";
import { blogPostMetadata } from "@/lib/blogMetadata";
import { getBlogPostMeta } from "@/lib/blogPosts";

const POST = getBlogPostMeta("confidence-limitations-read-diagnostic")!;
const DESCRIPTION =
  "Why partial scans and visible limitations build trust; how to read confidence, issues, and fixes without treating a score as a promise.";

export const metadata: Metadata = blogPostMetadata(POST, DESCRIPTION);

export default function BlogConfidenceLimitationsPage() {
  return (
    <>
      <BlogPostingJsonLd post={POST} description={DESCRIPTION} />
      <article className="blogArticle">
      <nav className="resultNavCrumb muted" aria-label="Breadcrumb">
        <Link href="/blog">Blog</Link>
        <span aria-hidden="true"> · </span>
        <span className="blogCrumbCurrent">Confidence and limitations</span>
      </nav>

      <header className="blogArticleHeader">
        <h1 className="resultTitle">Confidence and limitations: how to read a diagnostic honestly</h1>
        <p className="blogByline muted small">
          <span>GeoScore team</span>
          <span aria-hidden="true"> · </span>
          <time dateTime="2026-04-20">20 April 2026</time>
        </p>
        <p className="muted blogDeck">
          Most tools want you to believe every number is equally solid. A serious single-page diagnostic should tell you
          when the snapshot was thin, blocked, or ambiguous — and <strong>lower confidence</strong> instead of padding
          the score. That is not an apology; it is how you avoid false certainty before a launch or a client conversation.
        </p>
      </header>

      <section className="card block" aria-labelledby="blog-why">
        <h2 className="h2" id="blog-why">
          Why “limitations” belong next to the score
        </h2>
        <p className="muted">
          A URL analysis always depends on <strong>what was actually captured</strong>: render quality, how much of the
          page could be extracted, whether the page type is obvious, and whether optional semantic steps ran. When any
          of that is weak, pretending you have a full picture is worse than admitting the gap. Limitations are the
          honest inventory of what the run did <em>not</em> fully see — so you do not ship or pitch based on invented
          precision.
        </p>
      </section>

      <section className="card block" aria-labelledby="blog-confidence">
        <h2 className="h2" id="blog-confidence">
          What confidence is trying to tell you
        </h2>
        <p className="muted">
          <strong>Confidence</strong> is a summary of how much you should lean on the headline numbers and issue list
          for <em>this</em> run. High confidence usually means the render and extraction look complete enough that the
          rules fired on real signals, not on placeholders. Low confidence does not mean “ignore the result” — it
          means <strong>weigh the findings with context</strong>: fix obvious gaps, rescan after changes, or validate
          manually where the tool flags uncertainty. That workflow matches how operators already work; the product
          should say it out loud.
        </p>
      </section>

      <section className="card block" aria-labelledby="blog-partial">
        <h2 className="h2" id="blog-partial">
          Partial runs and empty-looking outputs
        </h2>
        <p className="muted">
          When capture is partial, a rules-first engine may produce <strong>fewer issues</strong> than you expect — not
          because the page is perfect, but because there was less to observe. GeoScore handles that at the product layer:
          you still get a coherent report shape, including fallback guidance when limitations dominate, so a thin scan
          does not masquerade as a clean bill of health. Read the <strong>limitations</strong> block before you
          celebrate a quiet issue list.
        </p>
      </section>

      <section className="card block" aria-labelledby="blog-explainable">
        <h2 className="h2" id="blog-explainable">
          Explainable scores vs a single hype number
        </h2>
        <p className="muted">
          Scores should trace back to <strong>observable signals and triggered rules</strong>, not to a black box that
          moves 40 points because a model had a mood. Optional LLM steps, when present, are bounded: they cannot silently
          replace the deterministic story. If you want the full picture of how that split works in the product, read{" "}
          <Link href="/how-it-works">How scoring works</Link> — it is the same language you will see next to your
          results.
        </p>
      </section>

      <section className="card block" aria-labelledby="blog-practice">
        <h2 className="h2" id="blog-practice">
          A two-minute read of any diagnostic
        </h2>
        <ul className="hiwList muted">
          <li>
            <strong>Limitations first:</strong> What did this run not fully see?
          </li>
          <li>
            <strong>Confidence second:</strong> How hard should you lean on the scores?
          </li>
          <li>
            <strong>Issues and fixes third:</strong> What is concrete and tied to evidence on the page?
          </li>
          <li>
            <strong>Page type:</strong> Does the classification match what you intended this URL to be? If not,
            override when the product allows — “good” depends on intent.
          </li>
        </ul>
        <p className="muted">
          If you are not signed in yet, the{" "}
          <Link href="/report/demo-example">example report</Link> shows the same structure on sample data so you know
          what to expect before you paste your own URL.
        </p>
      </section>

      <p className="blogCta muted">
        <Link href="/#analyze" className="button">
          Analyze a URL
        </Link>
        {" · "}
        <Link href="/how-it-works">How scoring works</Link>
        {" · "}
        <Link href="/blog/homepage-readiness-bounded-checklist">Homepage checklist</Link>
        {" · "}
        <Link href="/blog">All posts</Link>
      </p>
    </article>
    </>
  );
}
