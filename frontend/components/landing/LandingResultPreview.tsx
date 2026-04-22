/** Static preview — illustrative only; not tied to live API data. */

export function LandingResultPreview() {
  return (
    <section className="landingSection" aria-labelledby="preview-heading">
      <h2 className="landingSectionTitle" id="preview-heading">
        What you get back
      </h2>
      <p className="landingSectionLead">
        A compact result: scores, confidence, and actionable notes — not a crowded dashboard.
      </p>
      <ul className="landingPortableList muted small" aria-label="Takeaway formats">
        <li>
          <strong className="landingPortableStrong">Share</strong> — public snapshot link when you enable it.
        </li>
        <li>
          <strong className="landingPortableStrong">Copy</strong> — one-line summary for Slack or email.
        </li>
        <li>
          <strong className="landingPortableStrong">Export</strong> — minimal JSON for Notion, tickets, or CI.
        </li>
      </ul>
      <div className="landingPreviewCard" role="group" aria-labelledby="preview-heading">
        <div className="landingPreviewScores">
          <div>
            <p className="landingPreviewLabel">Global</p>
            <p className="landingPreviewScore landingPreviewScore--lg">72</p>
          </div>
          <div>
            <p className="landingPreviewLabel">SEO</p>
            <p className="landingPreviewScore">74</p>
          </div>
          <div>
            <p className="landingPreviewLabel">GEO</p>
            <p className="landingPreviewScore">70</p>
          </div>
        </div>
        <p className="landingPreviewConfidence">
          <span className="landingPreviewConfLabel">Confidence</span> Medium — directional until capture is ideal.
        </p>
        <div className="landingPreviewCols">
          <div>
            <p className="landingPreviewColTitle">Top issues</p>
            <ul className="landingPreviewList">
              <li>Meta description missing or too short</li>
              <li>Primary heading could be clearer</li>
            </ul>
          </div>
          <div>
            <p className="landingPreviewColTitle">Top fixes</p>
            <ul className="landingPreviewList">
              <li>Add a unique meta description (120–160 characters)</li>
              <li>Align H1 with the main user intent</li>
            </ul>
          </div>
        </div>
        <p className="small muted landingPreviewDisclaimer">Illustrative preview — your page will vary.</p>
      </div>
    </section>
  );
}
