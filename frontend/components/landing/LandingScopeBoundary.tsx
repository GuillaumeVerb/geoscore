/**
 * Plain-language scope — utility tools stay credible when limits are obvious.
 */
export function LandingScopeBoundary() {
  return (
    <section className="landingSection landingScopeBoundary" aria-labelledby="scope-heading">
      <h2 className="landingSectionTitle" id="scope-heading">
        What GeoScore is for (and what it skips)
      </h2>
      <p className="landingSectionLead">
        Same idea as a small file converter: a narrow job, done honestly — so you know when to trust the output.
      </p>
      <div className="landingScopeGrid">
        <div className="landingScopeCol">
          <h3 className="landingScopeColTitle">Built for</h3>
          <ul className="landingScopeList">
            <li>One public URL at a time — landing, article, pricing, docs, etc.</li>
            <li>A fast read before ship, handoff, or a client question.</li>
            <li>Scores tied to rules you can inspect, plus confidence and capture limits.</li>
            <li>Outputs you can reuse: public link, one-line summary, minimal JSON export.</li>
          </ul>
        </div>
        <div className="landingScopeCol">
          <h3 className="landingScopeColTitle">Not built for</h3>
          <ul className="landingScopeList">
            <li>Whole-site crawls or internal link graphs at scale.</li>
            <li>Rank tracking, SERP history, or keyword volumes.</li>
            <li>Backlink databases or competitor link intelligence.</li>
            <li>A single opaque “AI score” with no rule trail.</li>
          </ul>
        </div>
      </div>
    </section>
  );
}
