"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { ExampleDemoPublicReportLayout } from "@/components/ExampleDemoPublicReportLayout";
import { CaptureQualityBanner } from "@/components/CaptureQualityBanner";
import { IssuesList } from "@/components/IssuesList";
import { LimitationsPanel } from "@/components/LimitationsPanel";
import { MockDataBanner } from "@/components/MockDataBanner";
import { PageTypeConfidenceCard } from "@/components/PageTypeConfidenceCard";
import { RecommendationsSection } from "@/components/RecommendationsSection";
import { ScoreHeader } from "@/components/ScoreHeader";
import { ScoreMethodNote } from "@/components/ScoreMethodNote";
import { SectionTitle } from "@/components/SectionTitle";
import { SummaryCard } from "@/components/SummaryCard";
import { SystemIssuesCard } from "@/components/SystemIssuesCard";
import { loadPublicReport } from "@/lib/loadScan";
import { scanStatusFromPublicReport } from "@/lib/publicReportMapper";
import {
  hasDegradationLimitations,
  orderRecommendationsForDisplay,
  partitionIssues,
} from "@/lib/scanPresentation";
import type { PublicReport } from "@/types/scan";

export type PublicReportPresentation = "shared" | "exampleDemo";

type Props = {
  publicId: string;
  /** Polished marketing layout for `/report/demo-example` only. */
  presentation?: PublicReportPresentation;
};

export function PublicReportView({ publicId, presentation = "shared" }: Props) {
  const searchParams = useSearchParams();
  const urlHint = searchParams.get("url") ?? undefined;

  const [report, setReport] = useState<PublicReport | null>(null);
  const [source, setSource] = useState<"api" | "mock" | null>(null);
  const [loading, setLoading] = useState(true);

  const isExampleDemo = presentation === "exampleDemo";

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
      <main className="resultMain" aria-busy="true" aria-label="Shared report">
        <p className="muted" role="status" aria-live="polite">
          Loading shared report…
        </p>
      </main>
    );
  }

  if (isExampleDemo) {
    return <ExampleDemoPublicReportLayout report={report} source={source} />;
  }

  const scan = scanStatusFromPublicReport(report);
  const lims = report.limitations ?? [];
  const degraded = hasDegradationLimitations(lims);
  const emphasizeConfidence = degraded || (report.analysis_confidence ?? "").toLowerCase() === "low";
  const { system: systemIssues, content: contentIssues } = partitionIssues(report.top_issues ?? []);
  const orderedRecs = orderRecommendationsForDisplay(report.top_fixes ?? [], {
    partial: degraded,
    hasDegradationLimitations: degraded,
  });

  return (
    <main className="resultMain">
      {source === "mock" ? <MockDataBanner message="Demo public report — live service unreachable or unknown link." /> : null}

      <nav className="resultNavCrumb muted" aria-label="Shared report navigation">
        <Link href="/">Home</Link>
        <span aria-hidden="true"> · </span>
        <Link href="/dashboard">Recent scans</Link>
      </nav>

      <header className="resultHeader">
        <h1 className="resultTitle">Shared report</h1>
        <p className="mono small muted">Public id · {publicId}</p>
        <p className="mono small muted">{report.submitted_url}</p>
        {report.analyzed_at ? <p className="small muted">Analyzed: {report.analyzed_at}</p> : null}
      </header>

      <section className="card block" aria-labelledby="pub-overview">
        <SectionTitle id="pub-overview">Scores</SectionTitle>
        <div className="resultScoreStatusMeta" style={{ marginBottom: "0.5rem" }}>
          <span className="statusPill statusPill--final">Shared snapshot</span>
        </div>
        <ScoreHeader scan={scan} />
        <ScoreMethodNote source={source} meta={report.meta} compact />
      </section>

      <CaptureQualityBanner visible={degraded} />

      <SummaryCard url={report.submitted_url} summary={report.summary} />

      <LimitationsPanel limitations={lims} prominent={degraded} />

      <PageTypeConfidenceCard scan={scan} emphasizeConfidence={emphasizeConfidence} />

      <SystemIssuesCard issues={systemIssues} />

      <section className="card block" aria-labelledby="pub-issues">
        <SectionTitle id="pub-issues">Top SEO &amp; GEO issues</SectionTitle>
        <IssuesList issues={contentIssues} variant="plain" showSeverity />
      </section>

      <section className="card block" aria-labelledby="pub-recs">
        <SectionTitle id="pub-recs">Top recommendations</SectionTitle>
        <RecommendationsSection items={orderedRecs} groupSystemFirst={degraded} />
      </section>
    </main>
  );
}
