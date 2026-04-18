import Link from "next/link";

export function LandingHero() {
  return (
    <header className="landingHero">
      <p className="landingProductName">GeoScore</p>
      <h1 className="landingHeadline">Paste a URL. Get a serious SEO & GEO score.</h1>
      <p className="landingSubhead">
        GeoScore evaluates technical readiness, clarity, extractability, citation readiness, and trust signals —
        without turning into a bloated SEO suite.
      </p>
      <p className="landingPositioningLine">
        See whether a page is ready to rank, be understood, and be cited in modern search environments.
      </p>
      <div className="landingHeroCtas">
        <a className="button" href="#analyze" aria-label="Analyze a URL: go to the URL input form">
          Analyze a URL
        </a>
        <Link className="button secondary" href="/report/demo-example" aria-label="Open example public report">
          Example report
        </Link>
      </div>
      <p className="landingHeroMetaLink muted small">
        <Link href="/how-it-works">How scoring works</Link>
        <span aria-hidden="true"> · </span>
        <span>Deterministic rules first — explainable scores</span>
        <span aria-hidden="true"> · </span>
        <span>Projects &amp; compare when signed in</span>
      </p>
    </header>
  );
}
