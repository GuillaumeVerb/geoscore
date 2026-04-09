/**
 * Static mock payloads when the API is offline or for /scan/preview.
 * Shapes align with ScanDetailResponse / PublicReport (api-design.md).
 */

import type { PublicReport, ScanIssue, ScanLimitation, ScanRecommendation, ScanStatus } from "@/types/scan";

const MOCK_ISSUES: ScanIssue[] = [
  {
    code: "META_DESC_MISSING",
    title: "Meta description missing or too short",
    description: "Search snippets and GEO summaries rely on a clear meta description.",
    severity: "high",
    impact_scope: "seo",
    fix_priority: 1,
  },
  {
    code: "H1_SINGLE",
    title: "Primary heading could be clearer",
    description: "One obvious H1 helps both users and extraction models understand intent.",
    severity: "medium",
    impact_scope: "geo",
    fix_priority: 2,
  },
];

const MOCK_RECOMMENDATIONS: ScanRecommendation[] = [
  {
    key: "add-meta",
    title: "Add a unique meta description (120–160 characters)",
    explanation: "Summarize the page in plain language; include the primary topic once.",
    impact_scope: "seo",
    priority: 1,
    effort: "low",
    expected_gain: "Better snippet control and clearer machine-readable summary",
  },
  {
    key: "h1-intent",
    title: "Align H1 with the main user intent",
    explanation: "Match the wording users and models would use to describe this page.",
    impact_scope: "geo",
    priority: 2,
    effort: "low",
    expected_gain: "Improved clarity for ranking and citation-style answers",
  },
];

const MOCK_LIMITATIONS: ScanLimitation[] = [
  {
    code: "MOCK_DATA",
    message: "Demo data only — connect the API for a real analysis.",
    severity: "info",
  },
];

export const PREVIEW_SCAN_ID = "preview";

function defaultUrl(hint?: string) {
  const u = hint?.trim();
  if (u) {
    try {
      const withScheme = u.startsWith("http") ? u : `https://${u}`;
      return { submitted: withScheme, normalized: withScheme };
    } catch {
      /* fall through */
    }
  }
  return { submitted: "https://example.com/page", normalized: "https://example.com/page" };
}

export function buildMockScanDetail(scanId: string, urlHint?: string): ScanStatus {
  const { submitted, normalized } = defaultUrl(urlHint);
  return {
    scan_id: scanId,
    status: "completed",
    page_type_detected: "landing_page",
    page_type_final: "landing_page",
    analysis_confidence: "medium",
    global_score: 72,
    seo_score: 74,
    geo_score: 70,
    strengths: ["Reasonable title length", "HTTPS available", "Mobile viewport present"],
    issues: MOCK_ISSUES,
    recommendations: MOCK_RECOMMENDATIONS,
    limitations: MOCK_LIMITATIONS,
    summary:
      "This page shows baseline SEO structure with room to improve discoverability and GEO clarity. " +
      "Scores are illustrative until the backend pipeline runs with real extraction and deterministic rules.",
    meta: {
      submitted_url: submitted,
      normalized_url: normalized,
      scoring_version: "v0-mock",
      ruleset_version: "v0-mock",
      llm_prompt_version: null,
    },
  };
}

export function buildMockPublicReport(publicId: string, urlHint?: string): PublicReport {
  const { submitted } = defaultUrl(urlHint);
  return {
    public_id: publicId,
    scan_id: "mock-scan",
    submitted_url: submitted,
    page_type: "landing_page",
    analysis_confidence: "medium",
    global_score: 72,
    seo_score: 74,
    geo_score: 70,
    top_issues: MOCK_ISSUES.slice(0, 2),
    top_fixes: MOCK_RECOMMENDATIONS.slice(0, 2),
    limitations: MOCK_LIMITATIONS,
    summary:
      "Public snapshot: illustrative GEO + SEO scores. Connect the API for live shared reports tied to a real scan.",
    analyzed_at: new Date().toISOString(),
    meta: { scoring_version: "v0-mock", ruleset_version: "v0-mock" },
  };
}
