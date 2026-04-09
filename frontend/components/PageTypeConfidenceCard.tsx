import type { ScanStatus } from "@/types/scan";

type Props = { scan: ScanStatus };

export function PageTypeConfidenceCard({ scan }: Props) {
  const finalType = scan.page_type_final ?? scan.page_type_detected;
  const detected = scan.page_type_detected;

  return (
    <section className="card" aria-labelledby="page-type-heading">
      <h2 className="h2" id="page-type-heading">
        Page type &amp; confidence
      </h2>
      <dl className="dlGrid">
        <dt>Page type (final)</dt>
        <dd className="mono">{finalType ?? "—"}</dd>
        <dt>Page type (detected)</dt>
        <dd className="mono">{detected ?? "—"}</dd>
        <dt>Analysis confidence</dt>
        <dd className="mono">{scan.analysis_confidence ?? "—"}</dd>
      </dl>
    </section>
  );
}
