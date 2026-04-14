import {
  hasDegradationLimitations,
  limitationHeadline,
  softenLimitationMessage,
  sortLimitationsForDisplay,
} from "@/lib/scanPresentation";
import type { ScanLimitation } from "@/types/scan";

type Props = {
  limitations: ScanLimitation[];
  /** When true, show a slightly stronger frame (e.g. private result partial). */
  prominent?: boolean;
  /** When false, hide limitation codes (cleaner shared / demo pages). */
  showCodes?: boolean;
};

export function LimitationsPanel({ limitations, prominent, showCodes = true }: Props) {
  if (!limitations.length) {
    return null;
  }

  const sorted = sortLimitationsForDisplay(limitations);
  const degraded = hasDegradationLimitations(limitations);

  return (
    <section
      className={`limitationsPanel ${prominent ? "limitationsPanel--prominent" : ""}`}
      aria-labelledby="limitations-heading"
    >
      <h2 className="h2" id="limitations-heading">
        Analysis limitations
      </h2>
      {degraded ? (
        <p className="limitationsIntro">
          These constraints affected what we could see of the page. They are separate from on-page SEO/GEO
          findings below.
        </p>
      ) : (
        <p className="limitationsIntro muted small">
          Context for this run — usually informational.
        </p>
      )}
      <ul className="limitationsList">
        {sorted.map((l) => (
          <li key={l.code} className="limitationRow">
            <span className="limitationHeadline">{limitationHeadline(l.code)}</span>
            {showCodes ? (
              <span className="limitationCode mono small muted"> · {l.code}</span>
            ) : null}
            <p className="limitationBody">{softenLimitationMessage(l.message)}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
