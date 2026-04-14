type Props = {
  url?: string;
  summary?: string | null;
  /** When false, omit the URL line (e.g. when the hero already shows it). */
  showSubmittedUrl?: boolean;
};

export function SummaryCard({ url, summary, showSubmittedUrl = true }: Props) {
  return (
    <section className="card" aria-labelledby="summary-heading">
      <h2 className="h2" id="summary-heading">
        Summary
      </h2>
      {summary ? (
        <p className="summaryBody">{summary}</p>
      ) : (
        <p className="muted">
          No summary in this response yet. It will appear when the API provides one (e.g. after aggregation
          or optional LLM).
        </p>
      )}
      {showSubmittedUrl && url ? (
        <p className="mono small" style={{ marginTop: "0.75rem", marginBottom: 0 }}>
          <span className="muted">URL:</span> {url}
        </p>
      ) : null}
    </section>
  );
}
