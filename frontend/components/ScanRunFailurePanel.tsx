import Link from "next/link";

/**
 * Actionable help when a run ends in `failed` — not a substitute for the status banner, but next steps.
 */
type Props = {
  errorCode?: string | null;
};

export function ScanRunFailurePanel({ errorCode }: Props) {
  const c = (errorCode ?? "").toUpperCase();

  let hint: string | null = null;
  if (c === "INSUFFICIENT_CAPTURE") {
    hint =
      "The page did not yield enough visible text after HTTP and optional headless render. The URL may be blocked, " +
      "heavily dynamic, or timing out. Try again later, test a simpler public URL, or check that the host allows automated access.";
  } else if (c === "HTTP_ERROR") {
    hint =
      "The server returned an error status. The page may require authentication, return 4xx/5xx, or block our fetch. " +
      "Confirm the URL works in a normal browser without logging in.";
  } else if (c === "FETCH_ERROR") {
    hint =
      "The network request failed before a full HTTP response (DNS, TLS, timeout, or connection reset). Check the URL " +
      "and your connection, then run a new analysis.";
  } else {
    hint =
      "The pipeline did not finish. Use “Rescan” to try again, or pick another public URL. If this keeps happening, the target may block automated access.";
  }

  return (
    <section className="card block failureHelpPanel" aria-labelledby="failure-help-heading">
      <h2 className="h2" id="failure-help-heading">
        What you can do
      </h2>
      <p className="muted small" style={{ maxWidth: "40rem", lineHeight: 1.55 }}>
        {hint}
      </p>
      <ul className="failureHelpLinks small">
        <li>
          <Link href="/how-it-works">How capture and scoring work</Link> — when to trust a run.
        </li>
        <li>
          <Link href="/blog/confidence-limitations-read-diagnostic">Confidence and limitations</Link> — how to read a
          diagnostic honestly.
        </li>
        <li>
          <Link href="/blog/honest-limits-utility-trust">Honest limits and utility trust</Link> — why saying what we
          could not see helps credibility.
        </li>
        <li>
          <Link href="/#analyze">Analyze another URL</Link> if you need a quick comparison.
        </li>
      </ul>
    </section>
  );
}
