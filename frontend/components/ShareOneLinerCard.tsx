"use client";

import { useState } from "react";

type Props = {
  line: string;
  /** When false, hide copy UI (e.g. scores not ready). */
  enabled?: boolean;
};

export function ShareOneLinerCard({ line, enabled = true }: Props) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    if (!enabled) return;
    try {
      await navigator.clipboard.writeText(line);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  }

  return (
    <section className="card block" aria-labelledby="share-one-line-heading">
      <h2 className="h2" id="share-one-line-heading">
        Share in one line
      </h2>
      <p className="small muted sectionLead">Slack, X, or email — one pasteable summary with URL host and scores.</p>
      <p className="mono small shareOneLiner__text">{line}</p>
      <button type="button" className="button secondary" onClick={copy} disabled={!enabled}>
        {copied ? "Copied" : "Copy text"}
      </button>
    </section>
  );
}
