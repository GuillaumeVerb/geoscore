import { ScoreHeader } from "@/components/ScoreHeader";
import { isFinalScanStatus, statusLabel } from "@/lib/scanPresentation";
import type { ScanStatus } from "@/types/scan";

type Props = { scan: ScanStatus };

export function ResultScoreStatusHeader({ scan }: Props) {
  const final = isFinalScanStatus(scan.status);
  const label = statusLabel(scan.status);

  return (
    <div className="resultScoreStatusHeader">
      <div className="resultScoreStatusMeta">
        <span className={`statusPill ${final ? "statusPill--final" : "statusPill--progress"}`}>{label}</span>
        {!final ? <span className="small muted"> — analysis may still be running</span> : null}
      </div>
      <ScoreHeader scan={scan} />
    </div>
  );
}
