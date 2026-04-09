"use client";

import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { ResultShell } from "@/components/ResultShell";
import { loadScanDetail } from "@/lib/loadScan";
import type { ScanStatus } from "@/types/scan";

type Props = { scanId: string };

export function ScanResultView({ scanId }: Props) {
  const searchParams = useSearchParams();
  const urlHint = searchParams.get("url") ?? undefined;

  const [scan, setScan] = useState<ScanStatus | null>(null);
  const [source, setSource] = useState<"api" | "mock" | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    loadScanDetail(scanId, urlHint).then(({ scan: s, source: src }) => {
      if (!cancelled) {
        setScan(s);
        setSource(src);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [scanId, urlHint]);

  const onLocalPageType = useCallback((pageType: string) => {
    setScan((prev) => (prev ? { ...prev, page_type_final: pageType } : prev));
  }, []);

  if (loading || !scan || !source) {
    return (
      <main className="resultMain">
        <p className="muted">Loading result…</p>
      </main>
    );
  }

  const urlDisplay =
    (typeof scan.meta?.normalized_url === "string" && scan.meta.normalized_url) ||
    (typeof scan.meta?.submitted_url === "string" && scan.meta.submitted_url) ||
    urlHint;

  return (
    <ResultShell
      scan={scan}
      routeScanId={scanId}
      source={source}
      urlDisplay={urlDisplay}
      onLocalPageType={onLocalPageType}
    />
  );
}
