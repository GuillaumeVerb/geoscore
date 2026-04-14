"use client";

import { usePathname, useRouter } from "next/navigation";
import { useId, useState } from "react";

import { ApiError, postJson } from "@/lib/api";
import { clearAuthSession, getAuthToken } from "@/lib/authStorage";
import { PREVIEW_SCAN_ID } from "@/lib/mockData";
import type { ScanStatus } from "@/types/scan";

/** POST /api/scans returns ScanResponse; we only need scan_id for navigation. */
type ScanCreateResponse = Pick<ScanStatus, "scan_id">;

type UrlSubmitFormProps = {
  /** Label for the submit button (e.g. landing: "Analyze a URL"). */
  submitButtonText?: string;
  /** Optional project UUID — attaches new scan to this project. */
  projectId?: string | null;
};

function isUnauthorizedApiError(e: unknown): boolean {
  if (e instanceof ApiError && e.status === 401) return true;
  const m = e instanceof Error ? e.message : String(e);
  const low = m.toLowerCase();
  return (
    /\b401\b/i.test(m) ||
    low.includes("not authenticated") ||
    low.includes("invalid or expired session")
  );
}

export function UrlSubmitForm({ submitButtonText = "Analyze", projectId = null }: UrlSubmitFormProps) {
  const router = useRouter();
  const pathname = usePathname();
  const fieldId = useId();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!getAuthToken()) {
      const q = typeof window !== "undefined" ? window.location.search : "";
      const returnTo = pathname === "/" ? "/#analyze" : `${pathname}${q}`;
      router.push(`/sign-in?returnTo=${encodeURIComponent(returnTo)}`);
      return;
    }
    setLoading(true);
    try {
      const body: { url: string; project_id?: string } = { url: url.trim() };
      if (projectId) body.project_id = projectId;
      const data = await postJson<ScanCreateResponse>("/api/scans", body);
      router.push(`/scan/${data.scan_id}`);
    } catch (e) {
      if (isUnauthorizedApiError(e)) {
        clearAuthSession();
        const q = typeof window !== "undefined" ? window.location.search : "";
        const returnTo = pathname === "/" ? "/#analyze" : `${pathname}${q}`;
        router.push(`/sign-in?returnTo=${encodeURIComponent(returnTo)}`);
        return;
      }
      const q = encodeURIComponent(url.trim());
      router.push(`/scan/${PREVIEW_SCAN_ID}?url=${q}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="stack" aria-busy={loading}>
      <label className="label" htmlFor={fieldId}>
        Page URL
      </label>
      <div className="row">
        <input
          id={fieldId}
          name="url"
          type="url"
          required
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="input"
          autoComplete="url"
          inputMode="url"
        />
        <button
          type="submit"
          className="button"
          disabled={loading}
          aria-label={loading ? "Submitting scan request, please wait" : submitButtonText}
        >
          {loading ? "…" : submitButtonText}
        </button>
      </div>
    </form>
  );
}
