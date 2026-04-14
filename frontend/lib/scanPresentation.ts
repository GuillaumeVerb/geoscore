/**
 * Presentation helpers for scan / public report UI (no scoring logic).
 */

import type { ScanIssue, ScanLimitation, ScanRecommendation } from "@/types/scan";

const SYSTEM_SCOPE = "system";

/** Limitation codes that imply capture/render degradation for public-report banner heuristics. */
export const DEGRADATION_LIMITATION_CODES = new Set([
  "FETCH_DEGRADED",
  "PARTIAL_PIPELINE",
  "PLAYWRIGHT_FAILED",
  "PLAYWRIGHT_NO_GAIN",
  "PLAYWRIGHT_DISABLED",
  "PLAYWRIGHT_NOT_INSTALLED",
  "THIN_PAGE",
]);

const LIMITATION_HEADLINES: Record<string, string> = {
  FETCH_DEGRADED: "Capture was incomplete",
  PARTIAL_PIPELINE: "Partial analysis run",
  PLAYWRIGHT_FAILED: "Headless rendering issue",
  PLAYWRIGHT_NO_GAIN: "Render did not improve content",
  PLAYWRIGHT_DISABLED: "JS rendering disabled",
  PLAYWRIGHT_NOT_INSTALLED: "Browser automation not available",
  THIN_PAGE: "Very little text extracted",
  MOCK_DATA: "Demo data",
  EXAMPLE_REPORT: "Sample analysis",
};

export function isSystemIssue(issue: ScanIssue): boolean {
  return (issue.impact_scope ?? "").toLowerCase() === SYSTEM_SCOPE;
}

export function isSystemRecommendation(rec: ScanRecommendation): boolean {
  return (rec.impact_scope ?? "").toLowerCase() === SYSTEM_SCOPE;
}

export function partitionIssues(issues: ScanIssue[]): { system: ScanIssue[]; content: ScanIssue[] } {
  const system: ScanIssue[] = [];
  const content: ScanIssue[] = [];
  for (const i of issues) {
    (isSystemIssue(i) ? system : content).push(i);
  }
  return { system, content };
}

export function partitionRecommendations(
  recs: ScanRecommendation[],
): { system: ScanRecommendation[]; content: ScanRecommendation[] } {
  const system: ScanRecommendation[] = [];
  const content: ScanRecommendation[] = [];
  for (const r of recs) {
    (isSystemRecommendation(r) ? system : content).push(r);
  }
  return { system, content };
}

/** System recommendations first when scan is partial or has degradation limitations. */
export function orderRecommendationsForDisplay(
  recs: ScanRecommendation[],
  opts: { partial: boolean; hasDegradationLimitations: boolean },
): ScanRecommendation[] {
  const { system, content } = partitionRecommendations(recs);
  if (opts.partial || opts.hasDegradationLimitations) {
    return [...system, ...content];
  }
  return [...recs];
}

export function hasDegradationLimitations(limitations: ScanLimitation[]): boolean {
  return limitations.some((l) => DEGRADATION_LIMITATION_CODES.has(l.code));
}

export function limitationHeadline(code: string): string {
  return LIMITATION_HEADLINES[code] ?? "Note";
}

/** Trim very long server messages (e.g. Playwright paths) for UI. */
export function softenLimitationMessage(message: string, maxLen = 220): string {
  const t = message.trim();
  if (t.length <= maxLen) return t;
  return `${t.slice(0, maxLen).trim()}…`;
}

export function confidencePresentation(confidence: string | null | undefined): {
  label: string;
  hint: string;
} {
  const c = (confidence ?? "").toLowerCase();
  if (c === "high") {
    return {
      label: "High confidence",
      hint: "Signals are based on a solid capture of the page.",
    };
  }
  if (c === "medium") {
    return {
      label: "Medium confidence",
      hint: "Some signals may be incomplete; treat scores as directional.",
    };
  }
  if (c === "low") {
    return {
      label: "Low confidence",
      hint: "Capture or content was thin; prioritize limitations before acting on scores.",
    };
  }
  return {
    label: "Confidence unknown",
    hint: "The API did not return a confidence level for this run.",
  };
}

export function statusLabel(status: string | undefined): string {
  const s = (status ?? "").toLowerCase();
  if (s === "completed") return "Completed";
  if (s === "partial") return "Partial analysis";
  if (s === "failed") return "Failed";
  if (!s) return "Unknown";
  return s.replace(/_/g, " ");
}

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

export function isFinalScanStatus(status: string | undefined): boolean {
  const s = (status ?? "").toLowerCase();
  return s === "completed" || s === "partial" || s === "failed";
}

export function isInProgressStatus(status: string | undefined): boolean {
  return NON_FINAL.has((status ?? "").toLowerCase());
}

export function sortLimitationsForDisplay(limitations: ScanLimitation[]): ScanLimitation[] {
  const rank = (sev: string | undefined) => {
    const s = (sev ?? "info").toLowerCase();
    if (s === "error" || s === "warning") return 0;
    return 1;
  };
  return [...limitations].sort((a, b) => rank(a.severity) - rank(b.severity));
}
