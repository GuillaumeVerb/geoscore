"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { IssuesList } from "@/components/IssuesList";
import { MockDataBanner } from "@/components/MockDataBanner";
import { PageTypeConfidenceCard } from "@/components/PageTypeConfidenceCard";
import { RecommendationsList } from "@/components/RecommendationsList";
import { ScoreHeader } from "@/components/ScoreHeader";
import { SectionTitle } from "@/components/SectionTitle";
import { SummaryCard } from "@/components/SummaryCard";
import { loadPublicReport } from "@/lib/loadScan";
import type { PublicReport, ScanStatus } from "@/types/scan";

type Props = { publicId: string };

function reportToScanShape(report: PublicReport): ScanStatus {
  return {
    scan_id: report.scan_id,
    status: "public",
    page_type_detected: report.page_type,
    page_type_final: report.page_type,
    analysis_confidence: report.analysis_confidence,
    global_score: report.global_score,
    seo_score: report.seo_score,
    geo_score: report.geo_score,
    strengths: [],
    issues: report.top_issues,
    recommendations: report.top_fixes,
    limitations: report.limitations,
    summary: report.summary,
    meta: report.meta,
  };
}

export function PublicReportView({ publicId }: Props) {
  const searchParams = useSearchParams();
  const urlHint = searchParams.get("url") ?? undefined;

  const [report, setReport] = useState<PublicReport | null>(null);
  const [source, setSource] = useState<"api" | "mock" | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    loadPublicReport(publicId, urlHint).then(({ report: r, source: s }) => {
      if (!cancelled) {
        setReport(r);
        setSource(s);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [publicId, urlHint]);

  if (loading || !report || !source) {
    return (
      <main className="resultMain">
        <p className="muted">Loading public report…</p>
      </main>
    );
  }

  const scan = reportToScanShape(report);

  return (
    <main className="resultMain">
      {source === "mock" ? <MockDataBanner message="Demo public report — API offline or unknown id." /> : null}

      <header className="resultHeader">
        <h1 className="resultTitle">Shared report</h1>
        <p className="mono small muted">Public id · {publicId}</p>
        <p className="mono small muted">{report.submitted_url}</p>
        {report.analyzed_at ? <p className="small muted">Analyzed: {report.analyzed_at}</p> : null}
      </header>

      <section className="card block" aria-labelledby="pub-scores">
        <SectionTitle id="pub-scores">Scores</SectionTitle>
        <ScoreHeader scan={scan} />
      </section>

      <PageTypeConfidenceCard scan={scan} />

      <SummaryCard url={report.submitted_url} summary={report.summary} />

      <section className="card block">
        <SectionTitle>Issues</SectionTitle>
        <IssuesList issues={report.top_issues} variant="plain" />
      </section>

      <section className="card block">
        <SectionTitle>Recommendations</SectionTitle>
        <RecommendationsList items={report.top_fixes} variant="plain" />
      </section>

      <section className="card block">
        <SectionTitle>Limitations</SectionTitle>
        {report.limitations.length ? (
          <ul className="list">
            {report.limitations.map((l) => (
              <li key={l.code}>
                {l.message}
                {l.severity ? <span className="muted"> ({l.severity})</span> : null}
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">No limitations listed.</p>
        )}
      </section>
    </main>
  );
}
