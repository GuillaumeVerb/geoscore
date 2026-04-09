import type { ScanStatus } from "@/types/scan";

type Props = { scan: ScanStatus; embedded?: boolean };

export function ScanStatusCard({ scan, embedded }: Props) {
  const inner = (
    <>
      <p className="mono" style={{ margin: 0 }}>
        {scan.status}
      </p>
      {scan.error_message ? <p className="error">{scan.error_message}</p> : null}
      {scan.error_code ? (
        <p className="small muted" style={{ marginBottom: 0 }}>
          Code: <span className="mono">{scan.error_code}</span>
        </p>
      ) : null}
    </>
  );

  if (embedded) {
    return <div className="stack">{inner}</div>;
  }

  return (
    <section className="card">
      <h2 className="h2">Scan status</h2>
      {inner}
    </section>
  );
}
