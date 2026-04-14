import Link from "next/link";

import { IssuesList } from "@/components/IssuesList";
import { LimitationsPanel } from "@/components/LimitationsPanel";
import { MockDataBanner } from "@/components/MockDataBanner";
import { PageTypeConfidenceCard } from "@/components/PageTypeConfidenceCard";
import { PageTypeSelector } from "@/components/PageTypeSelector";
import { RecommendationsSection } from "@/components/RecommendationsSection";
import { RescanButton } from "@/components/RescanButton";
import { ResultScoreStatusHeader } from "@/components/ResultScoreStatusHeader";
import { ScanStatusBanner } from "@/components/ScanStatusBanner";
import { ScanStatusCard } from "@/components/ScanStatusCard";
import { ScoreBreakdown } from "@/components/ScoreBreakdown";
import { SectionTitle } from "@/components/SectionTitle";
import { ScoreMethodNote } from "@/components/ScoreMethodNote";
import { ShareReportCard } from "@/components/ShareReportCard";
import { StrengthsList } from "@/components/StrengthsList";
import { SummaryCard } from "@/components/SummaryCard";
import { SystemIssuesCard } from "@/components/SystemIssuesCard";
import type { DataSource } from "@/lib/loadScan";
import {
  hasDegradationLimitations,
  isFinalScanStatus,
  orderRecommendationsForDisplay,
  partitionIssues,
} from "@/lib/scanPresentation";
import type { ScanStatus } from "@/types/scan";

type Props = {
  scan: ScanStatus;
  routeScanId: string;
  source: DataSource;
  urlDisplay?: string;
  onLocalPageType?: (pageType: string) => void;
  onRefetchScan: () => Promise<void>;
};

export function ResultShell({
  scan,
  routeScanId,
  source,
  urlDisplay,
  onLocalPageType,
  onRefetchScan,
}: Props) {
  const apiEnabled = source === "api";
  const limitations = scan.limitations ?? [];
  const issues = scan.issues ?? [];
  const recommendations = scan.recommendations ?? [];

  const statusKey = (scan.status ?? "").toLowerCase();
  const isPartial = statusKey === "partial";
  const isFailed = statusKey === "failed";
  const final = isFinalScanStatus(scan.status);
  const degraded = hasDegradationLimitations(limitations);
  const emphasizeConfidence =
    isPartial || degraded || (scan.analysis_confidence ?? "").toLowerCase() === "low";

  const { system: systemIssues, content: contentIssues } = partitionIssues(issues);
  const orderedRecs = orderRecommendationsForDisplay(recommendations, {
    partial: isPartial,
    hasDegradationLimitations: degraded,
  });
  const groupRecs = isPartial || degraded;

  const sparseContent = contentIssues.length === 0 && recommendations.length === 0 && !isFailed;
  const parentScanId = scan.meta?.parent_scan_id;
  const hasParentForCompare =
    typeof parentScanId === "string" && parentScanId.length > 0 && final && !isFailed;

  return (
    <main className="resultMain">
      {source === "mock" ? <MockDataBanner /> : null}

      <nav className="resultNavCrumb muted" aria-label="Scan result navigation">
        <Link href="/dashboard">Recent scans</Link>
        <span aria-hidden="true"> · </span>
        <Link href="/#analyze">Analyze a URL</Link>
      </nav>

      <header className="resultHeader">
        <h1 className="resultTitle">Scan result</h1>
        <p className="mono small muted">
          Scan <span className="mono">{routeScanId}</span>
        </p>
      </header>

      {!final ? (
        <section className="card block" aria-labelledby="pipeline-status">
          <SectionTitle id="pipeline-status">Scan progress</SectionTitle>
          <ScanStatusCard scan={scan} embedded />
        </section>
      ) : null}

      <section className="card block" aria-labelledby="overview-block">
        <SectionTitle id="overview-block">Scores &amp; status</SectionTitle>
        <ResultScoreStatusHeader scan={scan} />
        <ScoreMethodNote source={source} meta={scan.meta} compact />
      </section>

      <ScanStatusBanner status={scan.status} errorCode={scan.error_code} errorMessage={scan.error_message} />

      <SummaryCard url={urlDisplay} summary={scan.summary} />

      <LimitationsPanel limitations={limitations} prominent={isPartial || degraded} />

      <PageTypeConfidenceCard scan={scan} emphasizeConfidence={emphasizeConfidence} />

      <section className="card block" aria-labelledby="strengths-block">
        <SectionTitle id="strengths-block">Strengths</SectionTitle>
        <StrengthsList items={scan.strengths ?? []} variant="plain" />
      </section>

      <SystemIssuesCard issues={systemIssues} />

      <section className="card block" aria-labelledby="content-issues-block">
        <SectionTitle id="content-issues-block">SEO &amp; GEO issues</SectionTitle>
        <p className="small muted sectionLead">
          On-page signals and content quality — distinct from capture or pipeline notes above.
        </p>
        <IssuesList issues={contentIssues} variant="plain" showSeverity />
      </section>

      <section className="card block" aria-labelledby="rec-block">
        <SectionTitle id="rec-block">Recommendations</SectionTitle>
        <p className="small muted sectionLead">
          Prioritized suggestions. Capture-related actions appear first when the run was partial or degraded.
        </p>
        <RecommendationsSection items={orderedRecs} groupSystemFirst={groupRecs} />
      </section>

      {sparseContent && (isPartial || degraded) && !isFailed ? (
        <p className="small muted sparseHint" role="status">
          Few page-level issues were reported because the capture was limited. Address limitations and rescan
          for a fuller checklist.
        </p>
      ) : null}

      <ScoreBreakdown scores={scan.scores} />

      <PageTypeSelector
        scanId={routeScanId}
        current={scan.page_type_final ?? scan.page_type_detected}
        apiEnabled={apiEnabled}
        onLocalPageType={onLocalPageType}
        onAfterPatchSuccess={onRefetchScan}
      />

      <section className="card block">
        <SectionTitle>Actions</SectionTitle>
        <div className="row">
          <RescanButton scanId={routeScanId} apiEnabled={apiEnabled} onAfterRescan={onRefetchScan} />
          {hasParentForCompare ? (
            <Link href={`/scan/${routeScanId}/compare`} className="button secondary">
              Compare to previous run
            </Link>
          ) : null}
        </div>
      </section>

      <ShareReportCard scanId={routeScanId} apiEnabled={apiEnabled} onAfterCreate={onRefetchScan} />
    </main>
  );
}
