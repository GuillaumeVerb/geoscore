import type { Metadata } from "next";

import { loadPublicReport } from "@/lib/loadScan";
import type { PublicReport } from "@/types/scan";

const DESC_MAX = 175;

function truncate(text: string, max: number): string {
  const t = text.trim();
  if (t.length <= max) return t;
  return `${t.slice(0, max - 1)}…`;
}

function hostnameFromUrl(raw: string): string {
  try {
    return new URL(raw).hostname;
  } catch {
    return raw.slice(0, 80);
  }
}

function buildTitle(report: PublicReport): string {
  const host = hostnameFromUrl(report.submitted_url);
  const g = report.global_score != null ? Math.round(report.global_score) : null;
  const scorePart = g != null ? ` · global ${g}` : "";
  return `Shared report · ${host}${scorePart}`;
}

function buildDescription(report: PublicReport): string {
  if (report.summary && report.summary.trim()) {
    return truncate(report.summary.trim(), DESC_MAX);
  }
  const seo = report.seo_score != null ? Math.round(report.seo_score) : "—";
  const geo = report.geo_score != null ? Math.round(report.geo_score) : "—";
  const g = report.global_score != null ? Math.round(report.global_score) : "—";
  const conf = report.analysis_confidence?.trim() || "—";
  return truncate(
    `SEO ${seo}, GEO ${geo}, global ${g}. Confidence: ${conf}. Read-only snapshot from GeoScore.`,
    DESC_MAX,
  );
}

/** Metadata for shareable public report URLs (`/report/[publicId]`). */
export async function buildSharedReportMetadata(publicId: string): Promise<Metadata> {
  const { report } = await loadPublicReport(publicId);
  const path = `/report/${publicId}`;
  const title = buildTitle(report);
  const description = buildDescription(report);

  return {
    title,
    description,
    alternates: { canonical: path },
    openGraph: {
      type: "website",
      title,
      description,
      url: path,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
    robots: { index: true, follow: true },
  };
}
