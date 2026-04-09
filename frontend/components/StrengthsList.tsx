type Props = { items: string[]; variant?: "card" | "plain" };

export function StrengthsList({ items, variant = "card" }: Props) {
  const body = !items.length ? (
    <p className="muted">No strengths listed for this run.</p>
  ) : (
    <ul className="list">
      {items.map((s) => (
        <li key={s}>{s}</li>
      ))}
    </ul>
  );

  if (variant === "plain") {
    return body;
  }

  return (
    <section className="card">
      <h2 className="h2">Strengths</h2>
      {body}
    </section>
  );
}
