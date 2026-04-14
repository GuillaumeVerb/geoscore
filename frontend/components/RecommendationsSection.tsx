import { partitionRecommendations } from "@/lib/scanPresentation";
import type { ScanRecommendation } from "@/types/scan";

type Props = {
  items: ScanRecommendation[];
  /** When true, show capture/reliability group first when non-empty. */
  groupSystemFirst: boolean;
};

export function RecommendationsSection({ items, groupSystemFirst }: Props) {
  if (!items.length) {
    return (
      <div className="muted">
        <p>No recommendations for this run.</p>
        <p className="small">
          If the analysis was partial, improving capture (e.g. rendering or access) may surface actionable
          suggestions on a rescan.
        </p>
      </div>
    );
  }

  if (!groupSystemFirst) {
    return (
      <ul className="list">
        {items.map((r) => (
          <li key={r.key ?? r.title}>
            <strong>{r.title}</strong>
            {r.explanation ? <div className="muted small">{r.explanation}</div> : null}
          </li>
        ))}
      </ul>
    );
  }

  const { system, content } = partitionRecommendations(items);

  return (
    <div className="recGroups">
      {system.length ? (
        <div className="recGroup">
          <h3 className="recGroupTitle">Capture &amp; reliability</h3>
          <ul className="list tight">
            {system.map((r) => (
              <li key={r.key ?? r.title}>
                <strong>{r.title}</strong>
                {r.explanation ? <div className="muted small">{r.explanation}</div> : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {content.length ? (
        <div className="recGroup">
          {system.length ? <h3 className="recGroupTitle">Page improvements</h3> : null}
          <ul className="list tight">
            {content.map((r) => (
              <li key={r.key ?? r.title}>
                <strong>{r.title}</strong>
                {r.explanation ? <div className="muted small">{r.explanation}</div> : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
