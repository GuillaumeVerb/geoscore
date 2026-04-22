import Link from "next/link";

import { UrlSubmitForm } from "@/components/UrlSubmitForm";

/**
 * Homepage hero + analyze in one block — utility-first (think “converter” sites):
 * one headline, the form immediately, minimal chrome.
 */
export function LandingPrimaryTool() {
  return (
    <section className="landingPrimaryTool" id="analyze" aria-labelledby="primary-tool-heading">
      <p className="landingProductName">GeoScore</p>
      <h1 className="landingPrimaryTitle" id="primary-tool-heading">
        Paste a URL. Get SEO &amp; GEO scores for that page.
      </h1>
      <p className="landingPrimaryLeak muted small">
        One public page per run. Deterministic rules first, with visible confidence and limitations — not a full SEO
        suite.
      </p>

      <div className="landingInputCard landingPrimaryToolCard">
        <UrlSubmitForm submitButtonText="Analyze" />
        <p className="small muted landingInputHint">
          Sign in to run a scan. If the API is unreachable, you&apos;ll get a full demo result instead.
        </p>
        <p className="small muted landingInputHint" style={{ marginTop: "0.35rem" }}>
          <Link href="/dashboard">Recent scans</Link>
          <span aria-hidden="true"> · </span>
          <Link href="/report/demo-example">Example report</Link>
          <span aria-hidden="true"> · </span>
          <Link href="/how-it-works">How scoring works</Link>
        </p>
      </div>
    </section>
  );
}
