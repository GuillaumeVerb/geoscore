import {
  confidenceDriversFromScan,
  confidencePresentation,
  pageTypeResultFraming,
} from "@/lib/scanPresentation";
import type { ScanStatus } from "@/types/scan";

type Props = {
  scan: ScanStatus;
  /** Stronger visual weight for confidence (e.g. partial scans). */
  emphasizeConfidence?: boolean;
};

export function PageTypeConfidenceCard({ scan, emphasizeConfidence }: Props) {
  const finalType = scan.page_type_final ?? scan.page_type_detected;
  const detected = scan.page_type_detected;
  const conf = confidencePresentation(scan.analysis_confidence);
  const drivers = confidenceDriversFromScan(scan);
  const framing = pageTypeResultFraming(finalType);

  return (
    <section
      className={`card ${emphasizeConfidence ? "confidenceCard--emphasis" : ""}`}
      aria-labelledby="page-type-heading"
    >
      <h2 className="h2" id="page-type-heading">
        Page type &amp; confidence
      </h2>
      <div className={`confidenceStrip ${emphasizeConfidence ? "confidenceStrip--emphasis" : ""}`}>
        <span className="confidenceLabel">{conf.label}</span>
        <p className="confidenceHint small muted">{conf.hint}</p>
      </div>
      {framing ? (
        <p className="small muted" style={{ marginTop: "0.65rem" }}>
          {framing}
        </p>
      ) : null}
      <div style={{ marginTop: "0.85rem" }}>
        <h3 className="h3" style={{ fontSize: "0.95rem", marginBottom: "0.35rem" }}>
          Why this confidence level
        </h3>
        {drivers.length ? (
          <ul className="confidenceDriverList small">
            {drivers.map((d) => (
              <li key={d.code}>{d.label}</li>
            ))}
          </ul>
        ) : (
          <p className="small muted">
            No capture or classification caveats were flagged — confidence reflects a full deterministic pass on the
            extracted snapshot.
          </p>
        )}
      </div>
      <dl className="dlGrid" style={{ marginTop: "0.75rem" }}>
        <dt>Page type (final)</dt>
        <dd className="mono">{finalType ?? "—"}</dd>
        <dt>Page type (detected)</dt>
        <dd className="mono">{detected ?? "—"}</dd>
      </dl>
    </section>
  );
}
