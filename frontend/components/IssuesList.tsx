import type { ScanIssue } from "@/types/scan";

type Props = {
  issues: ScanIssue[];
  variant?: "card" | "plain";
  /** Show severity as a compact tag (for SEO/GEO content issues). */
  showSeverity?: boolean;
};

export function IssuesList({ issues, variant = "card", showSeverity }: Props) {
  const body = !issues.length ? (
    <p className="muted">No issues reported for this section.</p>
  ) : (
    <ul className="list">
      {issues.map((i) => (
        <li key={i.code}>
          <strong>{i.title}</strong>
          {showSeverity && i.severity ? (
            <span className="issueSeverity" data-severity={i.severity}>
              {i.severity}
            </span>
          ) : null}
          {i.description ? <span className="muted"> — {i.description}</span> : null}
        </li>
      ))}
    </ul>
  );

  if (variant === "plain") {
    return body;
  }

  return (
    <section className="card">
      <h2 className="h2">Issues</h2>
      {body}
    </section>
  );
}
