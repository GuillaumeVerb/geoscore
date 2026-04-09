/** Mirrors backend ScanDetailResponse / PublicReportResponse for UI scaffolding. */

export type ScanStatus = {
  scan_id: string;
  status: string;
  page_type_detected?: string | null;
  page_type_final?: string | null;
  analysis_confidence?: string | null;
  global_score?: number | null;
  seo_score?: number | null;
  geo_score?: number | null;
  strengths: string[];
  issues: ScanIssue[];
  recommendations: ScanRecommendation[];
  limitations: ScanLimitation[];
  /** Short narrative (LLM or template); optional until pipeline fills it */
  summary?: string | null;
  /** Structured scores when analysis completed */
  scores?: Record<string, unknown> | null;
  error_code?: string | null;
  error_message?: string | null;
  meta?: Record<string, unknown>;
};

export type ScanIssue = {
  code: string;
  title: string;
  description?: string;
  severity?: string;
  impact_scope?: string;
  fix_priority?: number;
};

export type ScanRecommendation = {
  key?: string | null;
  title: string;
  explanation?: string;
  impact_scope?: string;
  priority?: number;
  effort?: string;
  expected_gain?: string;
};

export type ScanLimitation = {
  code: string;
  message: string;
  severity?: string;
};

export type PublicReport = {
  public_id: string;
  scan_id: string;
  submitted_url: string;
  page_type?: string | null;
  analysis_confidence?: string | null;
  global_score?: number | null;
  seo_score?: number | null;
  geo_score?: number | null;
  scores?: Record<string, unknown> | null;
  top_issues: ScanIssue[];
  top_fixes: ScanRecommendation[];
  limitations: ScanLimitation[];
  /** Optional short summary for shared view */
  summary?: string | null;
  analyzed_at?: string | null;
  meta?: Record<string, unknown>;
};
