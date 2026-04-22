import Link from "next/link";

export function LandingFooterCta() {
  return (
    <section className="landingFooterCta" aria-labelledby="footer-cta-heading">
      <h2 className="landingFooterCtaTitle" id="footer-cta-heading">
        Another page to check?
      </h2>
      <p className="muted landingFooterCtaLead">Jump back to the URL field — same flow, no extra steps.</p>
      <div className="landingHeroCtas">
        <a className="button" href="#analyze" aria-label="Go to URL input at top of page">
          Paste URL
        </a>
        <Link className="button secondary" href="/dashboard">
          Recent scans
        </Link>
      </div>
    </section>
  );
}
