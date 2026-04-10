import { getJson } from "@/lib/api";
import { buildMockPublicReport, buildMockScanDetail, PREVIEW_SCAN_ID } from "@/lib/mockData";
import type { PublicReport, ScanStatus } from "@/types/scan";

export type DataSource = "api" | "mock";

/** Normalize API/mock payloads so the UI always has arrays and stable fields. */
export function normalizeScanDetail(raw: ScanStatus): ScanStatus {
  return {
    scan_id: String(raw.scan_id),
    status: String(raw.status ?? "unknown"),
    page_type_detected: raw.page_type_detected ?? null,
    page_type_final: raw.page_type_final ?? null,
    analysis_confidence: raw.analysis_confidence ?? null,
    global_score: raw.global_score ?? null,
    seo_score: raw.seo_score ?? null,
    geo_score: raw.geo_score ?? null,
    strengths: raw.strengths ?? [],
    issues: raw.issues ?? [],
    recommendations: raw.recommendations ?? [],
    limitations: raw.limitations ?? [],
    summary: raw.summary ?? null,
    scores: raw.scores ?? null,
    error_code: raw.error_code ?? null,
    error_message: raw.error_message ?? null,
    meta: raw.meta && typeof raw.meta === "object" ? raw.meta : {},
  };
}

/** Initial load: preview → mock; otherwise try API then mock fallback. Uses NEXT_PUBLIC_API_URL. */
export async function loadScanDetail(
  scanId: string,
  urlHint?: string,
): Promise<{ scan: ScanStatus; source: DataSource }> {
  if (scanId === PREVIEW_SCAN_ID) {
    return {
      scan: normalizeScanDetail(buildMockScanDetail(scanId, urlHint)),
      source: "mock",
    };
  }
  try {
    const scan = await getJson<ScanStatus>(`/api/scans/${scanId}`);
    return { scan: normalizeScanDetail(scan), source: "api" };
  } catch {
    return {
      scan: normalizeScanDetail(buildMockScanDetail(scanId, urlHint)),
      source: "mock",
    };
  }
}

/**
 * Refetch a single scan from the API only (no mock fallback).
 * Use after mutations so the UI stays aligned with the server.
 */
export async function fetchScanDetailFromApi(scanId: string): Promise<ScanStatus> {
  const scan = await getJson<ScanStatus>(`/api/scans/${scanId}`);
  return normalizeScanDetail(scan);
}

/** Align public API payloads with optional fields the UI reads (summary, arrays). */
export function normalizePublicReport(raw: PublicReport): PublicReport {
  return {
    ...raw,
    top_issues: raw.top_issues ?? [],
    top_fixes: raw.top_fixes ?? [],
    limitations: raw.limitations ?? [],
    summary: raw.summary ?? null,
    meta: raw.meta && typeof raw.meta === "object" ? raw.meta : {},
  };
}

export async function loadPublicReport(
  publicId: string,
  urlHint?: string,
): Promise<{ report: PublicReport; source: DataSource }> {
  try {
    const report = await getJson<PublicReport>(`/api/public-reports/${publicId}`);
    return { report: normalizePublicReport(report), source: "api" };
  } catch {
    return { report: buildMockPublicReport(publicId, urlHint), source: "mock" };
  }
}
