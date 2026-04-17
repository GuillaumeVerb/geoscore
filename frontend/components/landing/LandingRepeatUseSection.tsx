import Link from "next/link";

/**
 * Short V2 surface: projects + compare — landing only, no API coupling.
 */
export function LandingRepeatUseSection() {
  return (
    <section className="landingSection landingRepeat" aria-labelledby="repeat-use-heading">
      <h2 className="landingSectionTitle" id="repeat-use-heading">
        Same URL, over time
      </h2>
      <p className="landingSectionLead">
        GeoScore is not only a one-off check. Group scans into <strong>projects</strong>, rescan after you ship
        changes, then open <strong>compare to previous run</strong> to see whether scores and issues moved in the right
        direction — still explainable, still one page at a time.
      </p>

      <div className="landingRepeatGrid">
        <div className="landingRepeatCard">
          <h3 className="landingRepeatCardTitle">Projects</h3>
          <p className="landingRepeatCardBody">
            Organize runs by site or client. Filter the dashboard so the list matches how you work — fewer lost UUIDs
            when you revisit a launch.
          </p>
        </div>
        <div className="landingRepeatCard">
          <h3 className="landingRepeatCardTitle">Compare</h3>
          <p className="landingRepeatCardBody">
            After a rescan, open the compare view: Global, SEO, and GEO scores plus issues side by side with the prior
            run. It is a presentation diff on stored results — not a second hidden score engine.
          </p>
        </div>
      </div>

      <div className="landingBeforeStrip" aria-labelledby="before-after-label">
        <p className="landingBeforeStripLabel" id="before-after-label">
          Before / after at a glance <span className="landingBeforeStripHint">(illustrative)</span>
        </p>
        <div className="landingBeforeFlow">
          <div className="landingBeforeCard" aria-hidden="true">
            <span className="landingBeforeCardTag">Earlier run</span>
            <div className="landingBeforeScores">
              <span>
                <span className="landingBeforeScoreLabel">Global</span>
                <span className="landingBeforeScoreVal">64</span>
              </span>
              <span>
                <span className="landingBeforeScoreLabel">SEO</span>
                <span className="landingBeforeScoreVal">61</span>
              </span>
              <span>
                <span className="landingBeforeScoreLabel">GEO</span>
                <span className="landingBeforeScoreVal">68</span>
              </span>
            </div>
          </div>
          <span className="landingBeforeArrow" aria-hidden="true">
            →
          </span>
          <div className="landingBeforeCard landingBeforeCard--next" aria-hidden="true">
            <span className="landingBeforeCardTag">After your change</span>
            <div className="landingBeforeScores">
              <span>
                <span className="landingBeforeScoreLabel">Global</span>
                <span className="landingBeforeScoreVal">71</span>
              </span>
              <span>
                <span className="landingBeforeScoreLabel">SEO</span>
                <span className="landingBeforeScoreVal">69</span>
              </span>
              <span>
                <span className="landingBeforeScoreLabel">GEO</span>
                <span className="landingBeforeScoreVal">74</span>
              </span>
            </div>
          </div>
        </div>
        <p className="landingBeforeFoot muted small">
          Flow: analyze → adjust the page → <Link href="/#analyze">rescan</Link> → open compare from the result or
          dashboard.
        </p>
      </div>
    </section>
  );
}
