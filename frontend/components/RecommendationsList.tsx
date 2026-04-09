import type { ScanRecommendation } from "@/types/scan";

type Props = { items: ScanRecommendation[]; variant?: "card" | "plain" };

export function RecommendationsList({ items, variant = "card" }: Props) {
  const body = !items.length ? (
    <p className="muted">No recommendations yet.</p>
  ) : (
    <ul className="list">
      {items.map((r) => (
        <li key={r.key ?? r.title}>
          <strong>{r.title}</strong>
          {r.explanation ? <div className="muted small">{r.explanation}</div> : null}
        </li>
      ))}
    </ul>
  );

  if (variant === "plain") {
    return body;
  }

  return (
    <section className="card">
      <h2 className="h2">Recommendations</h2>
      {body}
    </section>
  );
}
