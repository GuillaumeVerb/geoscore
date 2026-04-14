import type { ScanIssue } from "@/types/scan";

type Props = {
  issues: ScanIssue[];
};

export function SystemIssuesCard({ issues }: Props) {
  if (!issues.length) {
    return null;
  }

  return (
    <section className="systemIssuesCard" aria-labelledby="system-issues-heading">
      <h2 className="h2" id="system-issues-heading">
        Capture &amp; analysis reliability
      </h2>
      <p className="systemIssuesIntro small muted">
        These items describe visibility or pipeline limits — not typical page-quality SEO/GEO issues.
      </p>
      <ul className="list tight">
        {issues.map((i) => (
          <li key={i.code}>
            <strong>{i.title}</strong>
            {i.description ? <div className="muted small">{i.description}</div> : null}
          </li>
        ))}
      </ul>
    </section>
  );
}
