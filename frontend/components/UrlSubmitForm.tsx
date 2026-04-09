"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { postJson } from "@/lib/api";
import { PREVIEW_SCAN_ID } from "@/lib/mockData";
import type { ScanStatus } from "@/types/scan";

/** POST /api/scans returns ScanResponse; we only need scan_id for navigation. */
type ScanCreateResponse = Pick<ScanStatus, "scan_id">;

export function UrlSubmitForm() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await postJson<ScanCreateResponse>("/api/scans", { url });
      router.push(`/scan/${data.scan_id}`);
    } catch {
      const q = encodeURIComponent(url.trim());
      router.push(`/scan/${PREVIEW_SCAN_ID}?url=${q}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="stack">
      <label className="label" htmlFor="url">
        Page URL
      </label>
      <div className="row">
        <input
          id="url"
          name="url"
          type="url"
          required
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="input"
          autoComplete="url"
        />
        <button type="submit" className="button" disabled={loading}>
          {loading ? "…" : "Analyze"}
        </button>
      </div>
    </form>
  );
}
