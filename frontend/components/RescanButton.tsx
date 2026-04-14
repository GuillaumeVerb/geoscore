"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { postJson } from "@/lib/api";

type RescanApiResponse = { scan_id?: string; parent_scan_id?: string; status?: string };

type Props = {
  scanId: string;
  apiEnabled?: boolean;
  /** When the API does not return a new scan id, reload the current scan. */
  onAfterRescan?: () => void | Promise<void>;
};

export function RescanButton({ scanId, apiEnabled = true, onAfterRescan }: Props) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function rescan() {
    if (!apiEnabled) return;
    setLoading(true);
    setError(null);
    try {
      const data = await postJson<RescanApiResponse>(`/api/scans/${scanId}/rescan`, {});
      const nextId = data.scan_id;
      if (nextId) {
        router.push(`/scan/${nextId}`);
        return;
      }
      await onAfterRescan?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Rescan failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack" aria-busy={loading}>
      <button
        type="button"
        className="button secondary"
        onClick={rescan}
        disabled={loading || !apiEnabled}
        title={!apiEnabled ? "Not available with offline demo data" : undefined}
        aria-label={loading ? "Starting rescan, please wait" : "Rescan this page"}
      >
        {loading ? "…" : "Rescan"}
      </button>
      {!apiEnabled ? <p className="small muted">Rescan isn&apos;t available while viewing offline demo data.</p> : null}
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
