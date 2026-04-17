import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "How scoring works",
  description:
    "How GeoScore measures SEO and GEO readiness: deterministic rules, explainable issues, confidence, and limitations — without black-box scoring.",
};

export default function HowItWorksPage() {
  return (
    <article className="hiwArticle">
      <header className="hiwHeader">
        <h1 className="resultTitle">How scoring works</h1>
        <p className="muted hiwLead">
          GeoScore is built to be <strong>simple on the surface</strong> and <strong>serious underneath</strong> — the
          opposite of a vague “AI visibility” toy.
        </p>
      </header>

      <section className="card block" aria-labelledby="hiw-what">
        <h2 className="h2" id="hiw-what">
          What you get from one URL
        </h2>
        <ul className="hiwList">
          <li>
            <strong>Global, SEO, and GEO scores</strong> — how well the page supports classic ranking signals and
            modern extractability / citation readiness.
          </li>
          <li>
            <strong>Issues and prioritized fixes</strong> — each issue maps to something you can change on the page.
          </li>
          <li>
            <strong>Page type and confidence</strong> — we show what we inferred, when you can override it, and how
            certain we are given capture and extraction quality.
          </li>
          <li>
            <strong>Limitations</strong> — when capture was partial or signals were thin, we say so instead of faking
            precision.
          </li>
        </ul>
      </section>

      <section className="card block" aria-labelledby="hiw-method">
        <h2 className="h2" id="hiw-method">
          Method (no black box)
        </h2>
        <p className="muted">
          Scoring is <strong>rules-first and deterministic</strong> for the core engine. Optional LLM steps are{" "}
          <strong>bounded</strong>: they cannot silently override the whole score. You always see limitations and
          confidence when the run is partial or constrained. Exact scoring and ruleset versions appear on each result
          (and public report) so a score stays traceable.
        </p>
      </section>

      <section className="card block" aria-labelledby="hiw-seo-geo">
        <h2 className="h2" id="hiw-seo-geo">
          SEO vs GEO
        </h2>
        <p className="muted">
          <strong>SEO</strong> focuses on classic search readiness (structure, technical signals, content signals we
          can observe from the page). <strong>GEO</strong> focuses on how well the page can be understood, summarized,
          and cited by modern retrieval systems — clarity, answerability, and trust-style signals we can measure from
          the same snapshot.
        </p>
      </section>

      <section className="card block" aria-labelledby="hiw-not">
        <h2 className="h2" id="hiw-not">
          What GeoScore is not
        </h2>
        <ul className="hiwList muted">
          <li>Not a bloated rank tracker or backlink database.</li>
          <li>Not a guarantee of rankings or AI citations.</li>
          <li>Not a substitute for your judgment on brand, legal, or product copy.</li>
        </ul>
      </section>

      <p className="hiwFooter muted small">
        <Link href="/#analyze">Analyze a URL</Link>
        {" · "}
        <Link href="/report/demo-example">Example report</Link>
        {" · "}
        <Link href="/">Home</Link>
      </p>
    </article>
  );
}
