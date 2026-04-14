import Link from "next/link";

import { CaptureQualityBanner } from "@/components/CaptureQualityBanner";
import { IssuesList } from "@/components/IssuesList";
import { LimitationsPanel } from "@/components/LimitationsPanel";
import { RecommendationsSection } from "@/components/RecommendationsSection";
import { ScoreMethodNote } from "@/components/ScoreMethodNote";
import { ScoreBreakdown } from "@/components/ScoreBreakdown";
import { SectionTitle } from "@/components/SectionTitle";
import { StrengthsList } from "@/components/StrengthsList";
import { SummaryCard } from "@/components/SummaryCard";
import { SystemIssuesCard } from "@/components/SystemIssuesCard";
import { scanStatusFromPublicReport } from "@/lib/publicReportMapper";
import {
  confidencePresentation,
  hasDegradationLimitations,
  orderRecommendationsForDisplay,
  partitionIssues,
} from "@/lib/scanPresentation";
import type { PublicReport } from "@/types/scan";

type DataSource = "api" | "mock";

function hostFromUrl(url: string): string {
  try {
    return new URL(url).hostname;
  } catch {
    return url;
  }
}

function formatAnalyzedAt(iso: string | null | undefined): string | null {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

function ExampleReportFraming({ source }: { source: DataSource }) {
  return (
    <div className="exampleReportFraming" role="region" aria-label="Example report notice">
      <p className="exampleReportFramingEyebrow">Example report</p>
      <p className="exampleReportFramingBody">
        Representative GeoScore output: same sections and score shape as a real shared report. If you see demo data,
        sign in on the homepage and run a scan on your URL.
      </p>
      {source === "mock" ? (
        <p className="exampleReportFramingNote small muted">
          Showing saved demo data. Sign in and run a scan from the homepage to analyze your own page.
        </p>
      ) : null}
    </div>
  );
}

function PublicDemoReportHero({ report }: { report: PublicReport }) {
  const conf = confidencePresentation(report.analysis_confidence);
  const host = hostFromUrl(report.submitted_url);
  const analyzed = formatAnalyzedAt(report.analyzed_at);
  const ruleset = report.meta?.ruleset_version;
  const scoring = report.meta?.scoring_version;

  return (
    <header className="publicDemoHero" aria-labelledby="demo-hero-heading">
      <h1 className="publicDemoHeroTitle" id="demo-hero-heading">
        {host}
      </h1>
      <p className="publicDemoHeroUrl mono small muted">{report.submitted_url}</p>
      <div className="publicDemoHeroMeta">
        <span className="statusPill statusPill--final">Completed</span>
        {analyzed ? <span className="small muted">Analyzed · {analyzed}</span> : null}
      </div>
      <div className="publicDemoHeroScores" role="group" aria-label="Scores">
        <div className="publicDemoHeroScoreBlock">
          <p className="publicDemoHeroScoreLabel">Global</p>
          <p className="publicDemoHeroScoreValue">{formatScore(report.global_score)}</p>
        </div>
        <div className="publicDemoHeroScoreBlock">
          <p className="publicDemoHeroScoreLabel">SEO</p>
          <p className="publicDemoHeroScoreValue publicDemoHeroScoreValue--md">{formatScore(report.seo_score)}</p>
        </div>
        <div className="publicDemoHeroScoreBlock">
          <p className="publicDemoHeroScoreLabel">GEO</p>
          <p className="publicDemoHeroScoreValue publicDemoHeroScoreValue--md">{formatScore(report.geo_score)}</p>
        </div>
      </div>
      <div className="publicDemoHeroConfidence">
        <p className="publicDemoHeroConfidenceLabel">{conf.label}</p>
        <p className="publicDemoHeroConfidenceHint small muted">{conf.hint}</p>
      </div>
      <dl className="publicDemoHeroDl">
        <dt>Page type</dt>
        <dd className="mono">{report.page_type ?? "—"}</dd>
      </dl>
      {ruleset || scoring ? (
        <p className="publicDemoHeroVersions mono small muted">
          {scoring ? <span>{String(scoring)}</span> : null}
          {scoring && ruleset ? " · " : null}
          {ruleset ? <span>{String(ruleset)}</span> : null}
        </p>
      ) : null}
    </header>
  );
}

function formatScore(v: number | null | undefined) {
  if (v === null || v === undefined) return "—";
  return String(v);
}

function DemoReportFooterCta() {
  return (
    <section className="demoReportFooterCta" aria-labelledby="demo-footer-cta-heading">
      <h2 className="demoReportFooterCtaTitle" id="demo-footer-cta-heading">
        Analyze your own page
      </h2>
      <p className="muted demoReportFooterCtaLead">
        Run GeoScore on a URL you care about — same scores, issues, and prioritized fixes.
      </p>
      <Link href="/#analyze" className="button">
        Try GeoScore on your URL
      </Link>
    </section>
  );
}

type Props = {
  report: PublicReport;
  source: DataSource;
};

export function ExampleDemoPublicReportLayout({ report, source }: Props) {
  const scan = scanStatusFromPublicReport(report);
  const lims = report.limitations ?? [];
  const degraded = hasDegradationLimitations(lims);
  const { system: systemIssues, content: contentIssues } = partitionIssues(report.top_issues ?? []);
  const orderedRecs = orderRecommendationsForDisplay(report.top_fixes ?? [], {
    partial: degraded,
    hasDegradationLimitations: degraded,
  });

  return (
    <main className="resultMain demoExampleReport">
      <nav className="resultNavCrumb muted" aria-label="Example report navigation">
        <Link href="/">Home</Link>
        <span aria-hidden="true"> · </span>
        <Link href="/dashboard">Recent scans</Link>
      </nav>
      <ExampleReportFraming source={source} />
      <PublicDemoReportHero report={report} />
      <ScoreMethodNote source={source} meta={report.meta} compact />

      <CaptureQualityBanner visible={degraded} />

      <SummaryCard url={report.submitted_url} summary={report.summary} showSubmittedUrl={false} />

      <LimitationsPanel limitations={lims} prominent={degraded} showCodes={false} />

      {(scan.strengths?.length ?? 0) > 0 ? (
        <section className="card block" aria-labelledby="demo-strengths-heading">
          <SectionTitle id="demo-strengths-heading">Strengths</SectionTitle>
          <StrengthsList items={scan.strengths ?? []} variant="plain" />
        </section>
      ) : null}

      <SystemIssuesCard issues={systemIssues} />

      <section className="card block" aria-labelledby="demo-issues-heading">
        <SectionTitle id="demo-issues-heading">Top SEO &amp; GEO issues</SectionTitle>
        <IssuesList issues={contentIssues} variant="plain" showSeverity />
      </section>

      <section className="card block" aria-labelledby="demo-recs-heading">
        <SectionTitle id="demo-recs-heading">Top recommendations</SectionTitle>
        <RecommendationsSection items={orderedRecs} groupSystemFirst={degraded} />
      </section>

      <ScoreBreakdown scores={scan.scores} />

      <DemoReportFooterCta />
    </main>
  );
}
