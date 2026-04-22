import type { ScanStatus } from "@/types/scan";

type Props = { scores: ScanStatus["scores"] };

function tier(score: number | undefined): "ok" | "warn" | "low" | "na" {
  if (score === undefined || Number.isNaN(score)) return "na";
  if (score >= 72) return "ok";
  if (score >= 48) return "warn";
  return "low";
}

function tierLabel(t: ReturnType<typeof tier>): string {
  if (t === "ok") return "Strong";
  if (t === "warn") return "Improve";
  if (t === "low") return "Priority";
  return "—";
}

export function CitationReadinessCard({ scores }: Props) {
  if (!scores || typeof scores !== "object") {
    return null;
  }
  const raw = scores as Record<string, unknown>;
  const geo = raw.geo_subscores;
  if (!geo || typeof geo !== "object") {
    return null;
  }
  const g = geo as Record<string, number>;
  const rows: { key: string; label: string; hint: string }[] = [
    {
      key: "citation_readiness",
      label: "Citation readiness",
      hint: "Headings, entities, and quotable structure for assistants.",
    },
    {
      key: "extractability",
      label: "Extractability",
      hint: "How cleanly models can pull facts and lists from the page.",
    },
    {
      key: "trust_entity",
      label: "Entity trust",
      hint: "Brand, authorship, and credibility signals.",
    },
    {
      key: "hero_clarity",
      label: "Intent clarity",
      hint: "Obvious topic and audience in titles and hero content.",
    },
  ];

  const visible = rows.filter((r) => typeof g[r.key] === "number");
  if (!visible.length) {
    return null;
  }

  return (
    <section className="card block" aria-labelledby="citation-pack-heading">
      <h2 className="h2" id="citation-pack-heading">
        GEO citation checklist
      </h2>
      <p className="small muted sectionLead">
        GEO sub-scores as a compact readiness view — same signals as the deterministic engine, not a second audit.
      </p>
      <ul className="citationChecklist">
        {visible.map((row) => {
          const val = g[row.key] as number;
          const tr = tier(val);
          return (
            <li key={row.key} className={`citationChecklist__row citationChecklist__row--${tr}`}>
              <div className="citationChecklist__head">
                <span className="citationChecklist__label">{row.label}</span>
                <span className="citationChecklist__badge mono small">{tierLabel(tr)}</span>
                <span className="citationChecklist__score mono small">{val.toFixed(1)}</span>
              </div>
              <p className="small muted citationChecklist__hint">{row.hint}</p>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
