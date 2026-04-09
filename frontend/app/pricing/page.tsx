export default function PricingPage() {
  return (
    <main className="resultMain">
      <h1 className="resultTitle">Pricing</h1>
      <p className="muted">Plans and Stripe billing will ship in a later milestone.</p>
      <section className="card block" style={{ marginTop: "1rem" }}>
        <h2 className="h2">Placeholder tiers</h2>
        <ul className="list muted small">
          <li>Free — limited scans (TBD)</li>
          <li>Pro — higher limits and exports (TBD)</li>
        </ul>
      </section>
    </main>
  );
}
