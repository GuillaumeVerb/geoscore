import type { PublicReport, ScanStatus } from "@/types/scan";

/** Map a public report API payload into the scan shape the score/summary components expect. */
export function scanStatusFromPublicReport(report: PublicReport): ScanStatus {
  return {
    scan_id: report.scan_id,
    status: "completed",
    page_type_detected: report.page_type,
    page_type_final: report.page_type,
    analysis_confidence: report.analysis_confidence,
    global_score: report.global_score,
    seo_score: report.seo_score,
    geo_score: report.geo_score,
    strengths: report.strengths ?? [],
    issues: report.top_issues,
    recommendations: report.top_fixes,
    limitations: report.limitations,
    summary: report.summary,
    meta: report.meta,
    scores: report.scores ?? null,
  };
}
