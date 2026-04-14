const PILLARS = [
  {
    title: "SEO foundations",
    body: "Titles, structure, internal links, and technical basics — the signals search engines still rely on.",
  },
  {
    title: "GEO readiness",
    body: "How clearly the page states intent, how easy it is to extract, and how citation-friendly the content feels.",
  },
  {
    title: "Explainable scoring",
    body: "Every issue maps to a fix. You see confidence and limitations, not a black box.",
  },
  {
    title: "Priority fixes",
    body: "Recommendations are ordered so you know what to tackle first, without drowning in noise.",
  },
] as const;

export function LandingValuePillars() {
  return (
    <section className="landingSection" aria-labelledby="pillars-heading">
      <h2 className="landingSectionTitle" id="pillars-heading">
        Why GeoScore
      </h2>
      <p className="landingSectionLead">
        One URL in. A structured read on how the page stands up for both classic search and AI-driven discovery.
      </p>
      <ul className="landingPillarGrid">
        {PILLARS.map((p) => (
          <li key={p.title} className="landingPillar">
            <h3 className="landingPillarTitle">{p.title}</h3>
            <p className="landingPillarBody">{p.body}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
