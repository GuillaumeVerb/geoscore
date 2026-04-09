import type { ScanIssue } from "@/types/scan";

type Props = { issues: ScanIssue[]; variant?: "card" | "plain" };

export function IssuesList({ issues, variant = "card" }: Props) {
  const body = !issues.length ? (
    <p className="muted">No issues reported.</p>
  ) : (
    <ul className="list">
      {issues.map((i) => (
        <li key={i.code}>
          <strong>{i.title}</strong>
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
