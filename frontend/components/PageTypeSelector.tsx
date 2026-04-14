"use client";

import { useEffect, useId, useState } from "react";

import { patchJson } from "@/lib/api";
import type { ScanStatus } from "@/types/scan";

const PAGE_TYPES = [
  "homepage",
  "landing_page",
  "product_page",
  "pricing_page",
  "article",
  "about_page",
  "app_page",
  "other",
] as const;

type Props = {
  scanId: string;
  current?: string | null;
  apiEnabled?: boolean;
  onLocalPageType?: (pageType: string) => void;
  onAfterPatchSuccess?: () => void | Promise<void>;
};

export function PageTypeSelector({
  scanId,
  current,
  apiEnabled = true,
  onLocalPageType,
  onAfterPatchSuccess,
}: Props) {
  const selectId = useId();
  const [value, setValue] = useState(current ?? "other");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setValue(current ?? "other");
  }, [current]);

  async function apply() {
    setPending(true);
    setError(null);
    if (!apiEnabled) {
      onLocalPageType?.(value);
      setPending(false);
      return;
    }
    try {
      await patchJson<ScanStatus>(`/api/scans/${scanId}/page-type`, { page_type: value });
      await onAfterPatchSuccess?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Update failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="card" aria-busy={pending}>
      <h2 className="h2">Page type override</h2>
      <p className="muted small">
        {apiEnabled
          ? "Sends PATCH to the API; rescoring runs when the backend implements it."
          : "Demo mode: applies locally only (no API)."}
      </p>
      <div className="row">
        <label htmlFor={selectId} className="label visuallyHidden">
          Page type
        </label>
        <select
          id={selectId}
          className="input"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        >
          {PAGE_TYPES.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <button
          type="button"
          className="button secondary"
          onClick={apply}
          disabled={pending}
          aria-label={pending ? "Applying page type, please wait" : "Apply page type override"}
        >
          {pending ? "…" : "Apply"}
        </button>
      </div>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
    </section>
  );
}
