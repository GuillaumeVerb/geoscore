import { IssuesList } from "@/components/IssuesList";
import { MockDataBanner } from "@/components/MockDataBanner";
import { PageTypeConfidenceCard } from "@/components/PageTypeConfidenceCard";
import { RecommendationsList } from "@/components/RecommendationsList";
import { RescanButton } from "@/components/RescanButton";
import { ScanStatusCard } from "@/components/ScanStatusCard";
import { ScoreHeader } from "@/components/ScoreHeader";
import { SectionTitle } from "@/components/SectionTitle";
import { ShareReportCard } from "@/components/ShareReportCard";
import { StrengthsList } from "@/components/StrengthsList";
import { SummaryCard } from "@/components/SummaryCard";
import type { DataSource } from "@/lib/loadScan";
import type { ScanStatus } from "@/types/scan";

import { PageTypeSelector } from "@/components/PageTypeSelector";

type Props = {
  scan: ScanStatus;
  routeScanId: string;
  source: DataSource;
  urlDisplay?: string;
  onLocalPageType?: (pageType: string) => void;
};

export function ResultShell({ scan, routeScanId, source, urlDisplay, onLocalPageType }: Props) {
  const apiEnabled = source === "api";
  const limitations = scan.limitations ?? [];

  return (
    <main className="resultMain">
      {source === "mock" ? <MockDataBanner /> : null}

      <header className="resultHeader">
        <h1 className="resultTitle">Result</h1>
        <p className="mono small muted">
          Scan <span className="mono">{routeScanId}</span>
          {scan.status ? (
            <>
              {" "}
              · <span className="mono">{scan.status}</span>
            </>
          ) : null}
        </p>
      </header>

      <section className="card block">
        <SectionTitle id="status-block">Status</SectionTitle>
        <ScanStatusCard scan={scan} embedded />
      </section>

      <section className="card block" aria-labelledby="scores-block">
        <SectionTitle id="scores-block">Scores</SectionTitle>
        <ScoreHeader scan={scan} />
      </section>

      <PageTypeConfidenceCard scan={scan} />

      <SummaryCard url={urlDisplay} summary={scan.summary} />

      <section className="card block" aria-labelledby="strengths-block">
        <SectionTitle id="strengths-block">Strengths</SectionTitle>
        <StrengthsList items={scan.strengths ?? []} variant="plain" />
      </section>

      <section className="card block" aria-labelledby="issues-block">
        <SectionTitle id="issues-block">Issues</SectionTitle>
        <IssuesList issues={scan.issues ?? []} variant="plain" />
      </section>

      <section className="card block" aria-labelledby="rec-block">
        <SectionTitle id="rec-block">Recommendations</SectionTitle>
        <RecommendationsList items={scan.recommendations ?? []} variant="plain" />
      </section>

      <section className="card block" aria-labelledby="lim-block">
        <SectionTitle id="lim-block">Limitations</SectionTitle>
        {limitations.length ? (
          <ul className="list">
            {limitations.map((l) => (
              <li key={l.code}>
                {l.message}
                {l.severity ? <span className="muted"> ({l.severity})</span> : null}
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">No limitations recorded for this run.</p>
        )}
      </section>

      <PageTypeSelector
        scanId={routeScanId}
        current={scan.page_type_final ?? scan.page_type_detected}
        apiEnabled={apiEnabled}
        onLocalPageType={onLocalPageType}
      />

      <section className="card block">
        <SectionTitle>Actions</SectionTitle>
        <div className="row">
          <RescanButton scanId={routeScanId} apiEnabled={apiEnabled} />
        </div>
      </section>

      <ShareReportCard scanId={routeScanId} apiEnabled={apiEnabled} />
    </main>
  );
}
