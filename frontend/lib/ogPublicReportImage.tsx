import { ImageResponse } from "next/og";

import type { PublicReport } from "@/types/scan";

export const REPORT_OG_IMAGE_SIZE = { width: 1200, height: 630 } as const;

const ACCENT = "#0f766e";
const BG = "#111827";

function formatUrlLine(raw: string): string {
  try {
    const u = new URL(raw);
    const path = u.pathname === "/" ? "" : u.pathname;
    const combined = u.hostname + path;
    return combined.length > 96 ? `${combined.slice(0, 93)}…` : combined;
  } catch {
    return raw.length > 96 ? `${raw.slice(0, 93)}…` : raw;
  }
}

function scoreLabel(n: number | null | undefined): string {
  if (n == null || Number.isNaN(n)) return "—";
  return String(Math.round(n));
}

export function createPublicReportOgImageResponse(report: PublicReport): ImageResponse {
  const urlLine = formatUrlLine(report.submitted_url);
  const g = scoreLabel(report.global_score);
  const s = scoreLabel(report.seo_score);
  const geo = scoreLabel(report.geo_score);

  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          justifyContent: "center",
          background: `linear-gradient(145deg, ${ACCENT} 0%, #0d5c56 42%, ${BG} 100%)`,
          padding: 64,
        }}
      >
        <div
          style={{
            fontSize: 22,
            fontWeight: 600,
            color: "rgba(255,255,255,0.78)",
            fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
            marginBottom: 16,
          }}
        >
          GeoScore · Shared report
        </div>
        <div
          style={{
            fontSize: 38,
            fontWeight: 600,
            lineHeight: 1.25,
            color: "#fff",
            maxWidth: 1040,
            fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
            letterSpacing: "-0.02em",
          }}
        >
          {urlLine}
        </div>
        <div
          style={{
            marginTop: 28,
            fontSize: 34,
            fontWeight: 600,
            color: "rgba(255,255,255,0.92)",
            fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
          }}
        >
          Global {g} · SEO {s} · GEO {geo}
        </div>
      </div>
    ),
    { ...REPORT_OG_IMAGE_SIZE },
  );
}
