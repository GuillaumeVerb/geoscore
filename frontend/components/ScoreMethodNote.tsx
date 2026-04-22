import Link from "next/link";

import { RULESET_VERSION_LABEL, SCORING_VERSION_LABEL } from "@/lib/productCopy";

export type ScoreMethodSource = "api" | "mock";

type Props = {
  source: ScoreMethodSource;
  meta?: Record<string, unknown> | null;
  /** Tighter spacing when nested inside another card. */
  compact?: boolean;
};

function metaString(meta: Record<string, unknown> | null | undefined, snake: string, camel: string): string | null {
  if (!meta) return null;
  const v = meta[snake] ?? meta[camel];
  if (v === undefined || v === null) return null;
  const s = String(v).trim();
  return s.length ? s : null;
}

export function ScoreMethodNote({ source, meta, compact }: Props) {
  const ruleset = metaString(meta, "ruleset_version", "rulesetVersion") ?? RULESET_VERSION_LABEL;
  const scoring = metaString(meta, "scoring_version", "scoringVersion") ?? SCORING_VERSION_LABEL;
  const extraction = metaString(meta, "extraction_version", "extractionVersion");

  const basis =
    source === "mock"
      ? "Illustrative data using the same score layout as a live run."
      : "Scores come from deterministic rules first (bounded LLM where configured), with visible limitations and confidence.";

  const versions = [extraction, scoring, ruleset].filter(Boolean).join(" · ");

  return (
    <div className={compact ? "scoreMethodNote scoreMethodNote--compact" : "scoreMethodNote"}>
      <p className="small muted" style={{ margin: 0 }}>
        {basis}{" "}
        <span className="mono">{versions}</span>
        {" · "}
        <Link href="/how-it-works">How scoring works</Link>
      </p>
    </div>
  );
}
