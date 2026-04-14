import { confidencePresentation } from "@/lib/scanPresentation";
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
      <dl className="dlGrid" style={{ marginTop: "0.75rem" }}>
        <dt>Page type (final)</dt>
        <dd className="mono">{finalType ?? "—"}</dd>
        <dt>Page type (detected)</dt>
        <dd className="mono">{detected ?? "—"}</dd>
      </dl>
    </section>
  );
}
