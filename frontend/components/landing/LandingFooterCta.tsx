import Link from "next/link";

export function LandingFooterCta() {
  return (
    <section className="landingFooterCta" aria-labelledby="footer-cta-heading">
      <h2 className="landingFooterCtaTitle" id="footer-cta-heading">
        Ready to check a page?
      </h2>
      <p className="muted landingFooterCtaLead">
        Paste a URL. Get a serious SEO & GEO score — then share a clean public report if you want.
      </p>
      <div className="landingHeroCtas">
        <a className="button" href="#analyze" aria-label="Analyze a URL: go to the URL input form">
          Analyze a URL
        </a>
        <Link className="button secondary" href="/report/demo-example">
          See example report
        </Link>
      </div>
    </section>
  );
}
