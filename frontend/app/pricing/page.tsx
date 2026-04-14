import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Pricing",
  description: "Simple GeoScore plans — fair limits for scans, history, and shareable reports.",
};

export default function PricingPage() {
  return (
    <main className="resultMain">
      <h1 className="resultTitle">Pricing</h1>
      <p className="muted" style={{ maxWidth: "36rem", lineHeight: 1.55 }}>
        Billing is not live yet. When it ships, plans will stay straightforward: bounded scans, clear limits, and
        room to grow without turning GeoScore into a bloated suite.
      </p>
      <section className="card block" style={{ marginTop: "1.25rem" }}>
        <h2 className="h2">Planned direction</h2>
        <ul className="list muted small" style={{ marginBottom: "1rem" }}>
          <li>Free — limited monthly scans and core result detail</li>
          <li>Solo / Pro — more scans, history, rescans, and public reports</li>
        </ul>
        <p className="small muted" style={{ marginBottom: "0.75rem" }}>
          Details and Stripe checkout will land in a dedicated billing milestone.
        </p>
        <Link href="/#analyze" className="button secondary">
          Analyze a URL
        </Link>
      </section>
    </main>
  );
}
