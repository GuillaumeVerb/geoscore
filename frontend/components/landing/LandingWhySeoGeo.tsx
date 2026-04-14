export function LandingWhySeoGeo() {
  return (
    <section className="landingSection landingSeoGeo" aria-labelledby="seo-geo-heading">
      <h2 className="landingSectionTitle" id="seo-geo-heading">
        Why SEO and GEO together
      </h2>
      <div className="landingSeoGeoGrid">
        <div className="landingSeoGeoItem">
          <h3 className="landingSeoGeoLabel">SEO</h3>
          <p className="landingSeoGeoCopy">
            Helps your page get found — structure, relevance, and technical hygiene still matter.
          </p>
        </div>
        <div className="landingSeoGeoItem">
          <h3 className="landingSeoGeoLabel">GEO</h3>
          <p className="landingSeoGeoCopy">
            Helps your page get understood and reused when people (and systems) summarize, compare, or cite sources.
          </p>
        </div>
        <div className="landingSeoGeoItem landingSeoGeoItem--span">
          <h3 className="landingSeoGeoLabel">GeoScore</h3>
          <p className="landingSeoGeoCopy">
            Measures both in one pass so you can improve ranking potential and real-world clarity without juggling two
            disconnected tools.
          </p>
        </div>
      </div>
    </section>
  );
}
