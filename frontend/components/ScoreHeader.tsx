import type { ScanStatus } from "@/types/scan";

type Props = { scan: ScanStatus };

/** Global / SEO / GEO only (confidence and page type live in ResultShell). */
export function ScoreHeader({ scan }: Props) {
  return (
    <div className="scoreHeader" role="group" aria-label="Scores">
      <div>
        <p className="muted">Global score</p>
        <p className="scoreBig">{formatScore(scan.global_score)}</p>
      </div>
      <div>
        <p className="muted">SEO score</p>
        <p className="score">{formatScore(scan.seo_score)}</p>
      </div>
      <div>
        <p className="muted">GEO score</p>
        <p className="score">{formatScore(scan.geo_score)}</p>
      </div>
    </div>
  );
}

function formatScore(v: number | null | undefined) {
  if (v === null || v === undefined) return "—";
  return String(v);
}
