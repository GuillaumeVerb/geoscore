import { isInProgressStatus, statusLabel } from "@/lib/scanPresentation";
import type { ScanStatus } from "@/types/scan";

type Props = { scan: ScanStatus; embedded?: boolean };

export function ScanStatusCard({ scan, embedded }: Props) {
  const running = isInProgressStatus(scan.status);
  const inner = (
    <>
      <p style={{ margin: 0 }}>
        <span className="statusPill">{statusLabel(scan.status)}</span>
        <span className="mono small muted" style={{ marginLeft: "0.35rem" }}>
          ({scan.status})
        </span>
      </p>
      {running ? (
        <p className="small muted" style={{ marginBottom: 0 }}>
          Pipeline step in progress — this page will update automatically.
        </p>
      ) : null}
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
