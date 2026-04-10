"use client";

import Link from "next/link";
import { useState } from "react";

import { postJson } from "@/lib/api";

type Props = {
  scanId: string;
  apiEnabled?: boolean;
  onAfterCreate?: () => void | Promise<void>;
};

export function ShareReportCard({ scanId, apiEnabled = true, onAfterCreate }: Props) {
  const [publicPath, setPublicPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function enableShare() {
    if (!apiEnabled) return;
    setLoading(true);
    setError(null);
    try {
      const res = await postJson<{ public_id: string; url_path: string }>(
        `/api/scans/${scanId}/public-report`,
        {},
      );
      setPublicPath(res.url_path);
      await onAfterCreate?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not create public link");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h2 className="h2">Share</h2>
      <button
        type="button"
        className="button secondary"
        onClick={enableShare}
        disabled={loading || !apiEnabled}
        title={!apiEnabled ? "Requires API" : undefined}
      >
        {loading ? "…" : "Create public link"}
      </button>
      {!apiEnabled ? <p className="small muted">Public links require a connected API.</p> : null}
      {publicPath ? (
        <p className="mono small">
          Open:{" "}
          <Link href={publicPath} prefetch={false}>
            {publicPath}
          </Link>
        </p>
      ) : null}
      {error ? <p className="error">{error}</p> : null}
    </section>
  );
}
