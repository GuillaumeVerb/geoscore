import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Pricing",
  description:
    "GeoScore target packaging: Free, Solo, and Pro — scans, projects, compare, public reports, history. Billing not live yet.",
};

const PLANS = ["Free", "Solo", "Pro"] as const;

/** Locked target packaging; enforcement waits on billing — see callout above the table. */
const MATRIX: { label: string; free: string; solo: string; pro: string }[] = [
  { label: "Scans / month", free: "10", solo: "100", pro: "300" },
  { label: "Projects", free: "2", solo: "10", pro: "25" },
  { label: "Compare to previous run", free: "Included", solo: "Included", pro: "Included" },
  { label: "Public reports", free: "Included", solo: "Included", pro: "Included" },
  { label: "History on dashboard", free: "30 days", solo: "Full history", pro: "Full history" },
];

export default function PricingPage() {
  return (
    <main className="resultMain">
      <h1 className="resultTitle">Pricing</h1>

      <p className="pricingCallout" role="note">
        <strong>Billing and checkout are not live.</strong> There is no Stripe flow and no plan enforcement yet. Until
        that ships, you have <strong>early access</strong> to the product at no charge. The table below is our{" "}
        <strong>target packaging</strong> — the limits we intend to attach to each plan once billing exists.
      </p>

      <p className="muted" style={{ maxWidth: "40rem", lineHeight: 1.55, marginTop: "1rem" }}>
        These values are <strong>commercial direction</strong>, not what the app enforces today. When we turn billing
        on, we will confirm currency, price, and any last-minute cap tweaks before anyone is charged.
      </p>

      <h2 className="h2 pricingMatrixSectionTitle">Target packaging</h2>
      <p className="small muted pricingMatrixSectionLead">
        Same features across tiers where listed; plans differ by volume and history depth. Nothing here is enforced until
        billing ships.
      </p>

      <div className="pricingTableWrap">
        <table className="pricingMatrix">
          <caption className="visuallyHidden">Target Free, Solo, and Pro packaging</caption>
          <thead>
            <tr>
              <th scope="col" className="pricingMatrixCorner" />
              {PLANS.map((name) => (
                <th key={name} scope="col" className="pricingMatrixPlan">
                  {name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {MATRIX.map((row) => (
              <tr key={row.label}>
                <th scope="row" className="pricingMatrixRowLabel">
                  {row.label}
                </th>
                <td>{row.free}</td>
                <td>{row.solo}</td>
                <td>{row.pro}</td>
              </tr>
            ))}
            <tr className="pricingMatrixMetaRow">
              <th scope="row" className="pricingMatrixRowLabel">
                Planned billing
              </th>
              <td>$0</td>
              <td>Paid monthly</td>
              <td>Paid monthly</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p className="small muted" style={{ marginTop: "0.85rem", maxWidth: "40rem" }}>
        Solo and Pro <strong>prices are not listed</strong> yet — only monthly paid vs free. Checkout will show real
        amounts when Stripe is connected. Free stays at $0 with the caps above once enforcement exists.
      </p>
      <p className="small muted" style={{ marginTop: "0.5rem", maxWidth: "40rem" }}>
        &quot;Full history&quot; means no fixed expiry window for Solo/Pro at billing launch; fair-use rules may still
        apply and will be spelled out then.
      </p>

      <section className="card block" style={{ marginTop: "1.35rem" }}>
        <h2 className="h2">Use GeoScore today</h2>
        <p className="small muted" style={{ marginBottom: "0.85rem" }}>
          No plan picker yet — start from the home page:
        </p>
        <div className="pricingCtas">
          <Link href="/#analyze" className="button" aria-label="Go to home and analyze a URL">
            Analyze a URL
          </Link>
          <Link href="/report/demo-example" className="button secondary">
            Example report
          </Link>
          <Link href="/how-it-works" className="button secondary">
            How scoring works
          </Link>
        </div>
      </section>

      <p className="muted small" style={{ marginTop: "1.25rem" }}>
        <Link href="/">Home</Link>
      </p>
    </main>
  );
}
