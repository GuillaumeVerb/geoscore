import type { ScanStatus } from "@/types/scan";

type Props = { scores: ScanStatus["scores"] };

export function ScoreBreakdown({ scores }: Props) {
  if (!scores || typeof scores !== "object") {
    return null;
  }

  const raw = scores as Record<string, unknown>;
  const seo = raw.seo_subscores;
  const geo = raw.geo_subscores;

  if (!seo || typeof seo !== "object" || !geo || typeof geo !== "object") {
    return null;
  }

  const seoEntries = Object.entries(seo as Record<string, number>);
  const geoEntries = Object.entries(geo as Record<string, number>);

  return (
    <section className="card block" aria-labelledby="breakdown-heading">
      <h2 className="h2" id="breakdown-heading">
        Score breakdown
      </h2>
      <div className="breakdownGrid">
        <div>
          <h3 className="breakdownSub">SEO pillars</h3>
          <dl className="dlGrid">
            {seoEntries.map(([k, v]) => (
              <BreakdownDlRow key={k} label={k} value={v} />
            ))}
          </dl>
        </div>
        <div>
          <h3 className="breakdownSub">GEO pillars</h3>
          <dl className="dlGrid">
            {geoEntries.map(([k, v]) => (
              <BreakdownDlRow key={k} label={k} value={v} />
            ))}
          </dl>
        </div>
      </div>
    </section>
  );
}

function BreakdownDlRow({ label, value }: { label: string; value: number }) {
  return (
    <>
      <dt>{label.replace(/_/g, " ")}</dt>
      <dd className="mono">{typeof value === "number" ? value.toFixed(1) : String(value)}</dd>
    </>
  );
}
