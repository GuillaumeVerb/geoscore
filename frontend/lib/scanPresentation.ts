/**
 * Presentation helpers for scan / public report UI (no scoring logic).
 */

import type { ScanIssue, ScanLimitation, ScanRecommendation, ScanStatus } from "@/types/scan";

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

function _scopeDisplayPriority(pageType: string | null | undefined, impactScope: string | undefined): number {
  const pt = (pageType ?? "").toLowerCase();
  const s = (impactScope ?? "").toLowerCase();
  const commercial = ["landing_page", "homepage", "product_page", "pricing_page"].includes(pt);
  if (commercial) {
    if (s === "geo") return 0;
    if (s === "seo") return 1;
    return 2;
  }
  if (pt === "article") {
    if (s === "seo") return 0;
    if (s === "geo") return 1;
    return 2;
  }
  return 0;
}

function _sortContentRecommendationsByPageType(
  content: ScanRecommendation[],
  pageType: string | null | undefined,
): ScanRecommendation[] {
  return [...content].sort((a, b) => {
    const pa = a.priority ?? 99;
    const pb = b.priority ?? 99;
    if (pa !== pb) return pa - pb;
    return _scopeDisplayPriority(pageType, a.impact_scope) - _scopeDisplayPriority(pageType, b.impact_scope);
  });
}

/** System recommendations first when scan is partial or has degradation limitations. */
export function orderRecommendationsForDisplay(
  recs: ScanRecommendation[],
  opts: { partial: boolean; hasDegradationLimitations: boolean; pageType?: string | null },
): ScanRecommendation[] {
  const { system, content } = partitionRecommendations(recs);
  const pageType = opts.pageType ?? null;
  const orderedContent = _sortContentRecommendationsByPageType(content, pageType);
  if (opts.partial || opts.hasDegradationLimitations) {
    return [...system, ...orderedContent];
  }
  return _sortContentRecommendationsByPageType(recs, pageType);
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

/** Short labels for “why confidence is not maximal” (aligned with deterministic scoring inputs). */
const CONFIDENCE_LIMIT_LABELS: Record<string, string> = {
  FETCH_DEGRADED: "Fetch or HTTP status limited what we could measure.",
  PARTIAL_PIPELINE: "Pipeline used partial or degraded capture (thin HTML, limits, or defences).",
  PLAYWRIGHT_FAILED: "Headless render failed — HTTP snapshot may miss client-rendered content.",
  PLAYWRIGHT_NO_GAIN: "Render ran but did not improve visible text vs HTTP.",
  PLAYWRIGHT_DISABLED: "JS rendering path was disabled — dynamic content may be missing.",
  PLAYWRIGHT_NOT_INSTALLED: "Browser automation unavailable — JS-heavy pages may be under-read.",
  THIN_PAGE: "Very little text was extracted — GEO/SEO evidence is thin.",
  MOCK_DATA: "Demo data — not a live capture.",
  EXAMPLE_REPORT: "Sample report — illustrative only.",
};

export type ConfidenceDriver = { code: string; label: string };

export function confidenceDriversFromScan(scan: {
  status?: string | null;
  limitations?: ScanLimitation[];
  page_type_detected?: string | null;
  page_type_final?: string | null;
}): ConfidenceDriver[] {
  const out: ConfidenceDriver[] = [];
  const seen = new Set<string>();

  const push = (code: string, label: string) => {
    if (seen.has(code)) return;
    seen.add(code);
    out.push({ code, label });
  };

  const lims = scan.limitations ?? [];
  const hasPartialLim = lims.some((l) => l.code === "PARTIAL_PIPELINE");

  if ((scan.status ?? "").toLowerCase() === "partial" && !hasPartialLim) {
    push(
      "status_partial",
      "Scan completed as partial — treat scores as directional until capture improves.",
    );
  }

  for (const lim of lims) {
    const mapped = CONFIDENCE_LIMIT_LABELS[lim.code];
    if (mapped) {
      push(`lim_${lim.code}`, mapped);
    } else {
      push(`lim_${lim.code}`, `${limitationHeadline(lim.code)}: ${softenLimitationMessage(lim.message, 140)}`);
    }
  }

  const det = (scan.page_type_detected ?? "").trim();
  const fin = (scan.page_type_final ?? "").trim();
  if (det && fin && det !== fin) {
    push(
      "page_type_override",
      "You chose a different page type than auto-detect — scoring weights follow your selection.",
    );
  }

  return out;
}

export function displayHostOrPath(url: string): string {
  const t = url.trim();
  if (!t) return "this page";
  try {
    const u = t.startsWith("http") ? new URL(t) : new URL(`https://${t}`);
    return u.hostname.replace(/^www\./, "") || t;
  } catch {
    return t.length > 48 ? `${t.slice(0, 45)}…` : t;
  }
}

export function buildShareOneLiner(input: {
  url: string;
  global_score?: number | null;
  seo_score?: number | null;
  geo_score?: number | null;
  topFixTitle?: string | null;
}): string {
  const host = displayHostOrPath(input.url);
  const g = input.global_score;
  const s = input.seo_score;
  const geo = input.geo_score;
  const scorePart =
    g != null && s != null && geo != null
      ? `Global ${Math.round(g)}/100 (SEO ${Math.round(s)}, GEO ${Math.round(geo)})`
      : g != null
        ? `Global ${Math.round(g)}/100`
        : "Scores pending";
  const fix = (input.topFixTitle ?? "").trim();
  const tail = fix ? ` Top fix: ${fix.endsWith(".") ? fix.slice(0, -1) : fix}.` : "";
  return `GeoScore — ${host}: ${scorePart}.${tail}`;
}

export function buildMinimalScanExport(input: {
  scanId: string;
  url: string;
  scan: Pick<
    ScanStatus,
    | "status"
    | "page_type_detected"
    | "page_type_final"
    | "global_score"
    | "seo_score"
    | "geo_score"
    | "summary"
    | "issues"
    | "recommendations"
    | "limitations"
    | "scores"
    | "meta"
  >;
  oneLiner?: string;
}): Record<string, unknown> {
  const { scan, scanId, url, oneLiner } = input;
  const meta = scan.meta ?? {};
  return {
    schema: "geoscore.scan_export.v1",
    scan_id: scanId,
    url,
    status: scan.status,
    page_type: scan.page_type_final ?? scan.page_type_detected ?? null,
    scores: {
      global: scan.global_score ?? null,
      seo: scan.seo_score ?? null,
      geo: scan.geo_score ?? null,
      breakdown: scan.scores ?? null,
    },
    summary: scan.summary ?? null,
    share_one_liner: oneLiner ?? null,
    issues: (scan.issues ?? []).map((i) => ({
      code: i.code,
      title: i.title,
      severity: i.severity ?? null,
      impact_scope: i.impact_scope ?? null,
    })),
    recommendations: (scan.recommendations ?? []).map((r) => ({
      key: r.key ?? null,
      title: r.title,
      impact_scope: r.impact_scope ?? null,
      priority: r.priority ?? null,
    })),
    limitations: scan.limitations ?? [],
    versions: {
      extraction: meta.extraction_version ?? meta.extractionVersion ?? null,
      scoring: meta.scoring_version ?? meta.scoringVersion ?? null,
      ruleset: meta.ruleset_version ?? meta.rulesetVersion ?? null,
      llm_prompt: meta.llm_prompt_version ?? meta.llmPromptVersion ?? null,
    },
    meta_timestamps: {
      completed_at: meta.completed_at ?? meta.completedAt ?? null,
    },
  };
}

export function pageTypeResultFraming(pageType: string | null | undefined): string | null {
  const pt = (pageType ?? "").toLowerCase();
  if (!pt) return null;
  if (pt === "landing_page" || pt === "homepage") {
    return "For this surface, fixes are ordered with commercial clarity first (hero, offer, trust), then discoverability.";
  }
  if (pt === "product_page" || pt === "pricing_page") {
    return "For this surface, offer precision and trust cues are weighted ahead of generic content-depth nags.";
  }
  if (pt === "article") {
    return "For editorial pages, structure and depth lead the checklist; commercial hero nags are de-emphasized.";
  }
  if (pt === "about_page") {
    return "For about-style pages, entity trust and clarity matter more than conversion-style hero checks.";
  }
  if (pt === "app_page") {
    return "For app or product UI pages, extractability and intent labels matter more than classic article signals.";
  }
  return null;
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
