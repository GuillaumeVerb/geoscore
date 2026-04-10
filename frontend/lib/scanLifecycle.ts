/**
 * Scan status lifecycle (docs/01-architecture/api-design.md).
 * Polling runs until a terminal status is reached.
 */

const NON_FINAL = new Set([
  "created",
  "queued",
  "fetching",
  "rendering",
  "extracting",
  "scoring_rules",
  "scoring_llm",
  "aggregating",
]);

const FINAL = new Set(["completed", "partial", "failed"]);

export function isScanStatusNonFinal(status: string | null | undefined): boolean {
  if (!status) return true;
  return NON_FINAL.has(status);
}

export function isScanStatusFinal(status: string | null | undefined): boolean {
  if (!status) return false;
  return FINAL.has(status);
}

/** Polling interval when waiting on the pipeline (ms). */
export const SCAN_POLL_INTERVAL_MS = 2500;
