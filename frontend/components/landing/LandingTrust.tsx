const POINTS = [
  "Deterministic rules first — scoring you can reason about.",
  "LLM is optional, bounded, and never drives the core score.",
  "Confidence and limitations are always visible when analysis is uncertain.",
  "No black-box score: issues, recommendations, and versions are explicit.",
] as const;

export function LandingTrust() {
  return (
    <section className="landingSection landingTrust" aria-labelledby="trust-heading">
      <h2 className="landingSectionTitle" id="trust-heading">
        Built to be credible
      </h2>
      <ul className="landingTrustList">
        {POINTS.map((t) => (
          <li key={t}>{t}</li>
        ))}
      </ul>
    </section>
  );
}
