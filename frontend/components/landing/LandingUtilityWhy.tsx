/**
 * Single condensed “why” block — fewer marketing sections, same substance.
 */
export function LandingUtilityWhy() {
  return (
    <section className="landingSection" aria-labelledby="utility-why-heading">
      <h2 className="landingSectionTitle" id="utility-why-heading">
        What one scan covers
      </h2>
      <p className="landingSectionLead">
        SEO and GEO in one pass: classic discoverability plus how machines would quote or summarize the page.
      </p>
      <ul className="landingUtilityGrid">
        <li className="landingUtilityCell">
          <h3 className="landingUtilityLabel">SEO</h3>
          <p className="landingUtilityBody">Structure, titles, basics, and hygiene signals search engines still lean on.</p>
        </li>
        <li className="landingUtilityCell">
          <h3 className="landingUtilityLabel">GEO</h3>
          <p className="landingUtilityBody">Intent clarity, extractability, citation-friendly structure, and light trust cues.</p>
        </li>
        <li className="landingUtilityCell">
          <h3 className="landingUtilityLabel">Explainable</h3>
          <p className="landingUtilityBody">Issues map to fixes; versions are shown; LLM stays bounded when present.</p>
        </li>
        <li className="landingUtilityCell">
          <h3 className="landingUtilityLabel">Prioritized</h3>
          <p className="landingUtilityBody">Recommendations are capped and ordered so the list stays actionable.</p>
        </li>
      </ul>
    </section>
  );
}
