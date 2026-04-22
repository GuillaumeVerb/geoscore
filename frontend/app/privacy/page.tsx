import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy & data",
  description:
    "What GeoScore processes when you submit a URL: analysis inputs, storage, and what we do not do with your scans.",
};

export default function PrivacyPage() {
  return (
    <main className="resultMain legalPage">
      <header className="resultHeader">
        <h1 className="resultTitle">Privacy and data</h1>
        <p className="muted small" style={{ maxWidth: "40rem" }}>
          Short and practical. GeoScore is built as a small analysis utility, not a data broker.
        </p>
      </header>

      <section className="card block" aria-labelledby="p-what">
        <h2 className="h2" id="p-what">
          What we process
        </h2>
        <p className="muted">
          When you start a scan, we use the <strong>URL you provide</strong> to fetch the page (HTTP, and sometimes
          headless rendering) and to extract structured signals for SEO and GEO scoring. That typically includes
          public HTML, text, and metadata visible to a normal or automated access path — the same class of data you
          would already expose to visitors and crawlers.
        </p>
      </section>

      <section className="card block" aria-labelledby="p-store">
        <h2 className="h2" id="p-store">
          What we keep in your account
        </h2>
        <p className="muted">
          For signed-in users, we <strong>store the scan result</strong> (scores, issues, recommendations, limitations,
          and related metadata) so you can return to it, rescan, compare runs, and share a public report when you choose
          to. We do not need your marketing list or PII to run a URL check.
        </p>
      </section>

      <section className="card block" aria-labelledby="p-not">
        <h2 className="h2" id="p-not">
          What we do not claim
        </h2>
        <p className="muted">
          Running GeoScore is <strong>not</strong> legal advice, does not replace your privacy policy on your own site,
          and does not by itself make you “GDPR compliant” — you remain responsible for your properties and for how you
          use third-party tools. If you need a formal DPA for a company deployment, use your own legal review; this page
          is a product description, not a contract.
        </p>
      </section>

      <p className="small muted" style={{ marginTop: "1.5rem" }}>
        <Link href="/">← Home</Link>
      </p>
    </main>
  );
}
