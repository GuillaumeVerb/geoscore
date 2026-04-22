import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="siteFooter" role="contentinfo">
      <p className="siteFooterLine small muted">
        <span>
          GeoScore processes the URL you submit to fetch and analyze that page for SEO/GEO signals. We do not use your
          scan to train public models.{" "}
          <Link href="/privacy" className="siteFooterLink">
            Privacy &amp; data
          </Link>
        </span>
        <span className="siteFooterSep" aria-hidden="true">
          {" "}
          ·{" "}
        </span>
        <Link href="/" className="siteFooterLink">
          Home
        </Link>
        {" · "}
        <Link href="/blog" className="siteFooterLink">
          Blog
        </Link>
      </p>
    </footer>
  );
}
