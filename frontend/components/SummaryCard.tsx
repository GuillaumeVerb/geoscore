type Props = {
  url?: string;
  summary?: string | null;
};

export function SummaryCard({ url, summary }: Props) {
  return (
    <section className="card" aria-labelledby="summary-heading">
      <h2 className="h2" id="summary-heading">
        Summary
      </h2>
      {summary ? (
        <p className="summaryBody">{summary}</p>
      ) : (
        <p className="muted">
          A short narrative will appear here once analysis completes (deterministic signals + optional LLM).
        </p>
      )}
      {url ? (
        <p className="mono small" style={{ marginTop: "0.75rem", marginBottom: 0 }}>
          <span className="muted">URL:</span> {url}
        </p>
      ) : null}
    </section>
  );
}
