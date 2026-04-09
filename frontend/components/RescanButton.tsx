"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { postJson } from "@/lib/api";

type RescanApiResponse = { scan_id: string; parent_scan_id: string; status: string };

type Props = { scanId: string; apiEnabled?: boolean };

export function RescanButton({ scanId, apiEnabled = true }: Props) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function rescan() {
    if (!apiEnabled) return;
    setLoading(true);
    setError(null);
    try {
      const data = await postJson<RescanApiResponse>(`/api/scans/${scanId}/rescan`, {});
      router.push(`/scan/${data.scan_id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Rescan failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <button
        type="button"
        className="button secondary"
        onClick={rescan}
        disabled={loading || !apiEnabled}
        title={!apiEnabled ? "Requires API" : undefined}
      >
        {loading ? "…" : "Rescan"}
      </button>
      {!apiEnabled ? <p className="small muted">Rescan needs a connected API.</p> : null}
      {error ? <p className="error">{error}</p> : null}
    </div>
  );
}
