"use client";

import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

import { ResultShell } from "@/components/ResultShell";
import { fetchScanDetailFromApi, loadScanDetail, type DataSource } from "@/lib/loadScan";
import { PREVIEW_SCAN_ID } from "@/lib/mockData";
import { isScanStatusNonFinal, SCAN_POLL_INTERVAL_MS } from "@/lib/scanLifecycle";
import type { ScanStatus } from "@/types/scan";

type Props = { scanId: string };

export function ScanResultView({ scanId }: Props) {
  const searchParams = useSearchParams();
  const urlHint = searchParams.get("url") ?? undefined;

  const [scan, setScan] = useState<ScanStatus | null>(null);
  const [source, setSource] = useState<DataSource | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  /** Single reload entry point: preview/mock path, or API-only refetch. */
  const refetchScan = useCallback(async () => {
    if (scanId === PREVIEW_SCAN_ID) {
      const { scan: s, source: src } = await loadScanDetail(scanId, urlHint);
      if (!mounted.current) return;
      setScan(s);
      setSource(src);
      return;
    }
    setIsRefreshing(true);
    try {
      const s = await fetchScanDetailFromApi(scanId);
      if (!mounted.current) return;
      setScan(s);
      setSource("api");
    } catch {
      /* keep current scan; avoid swapping to mock after user had live data */
    } finally {
      if (mounted.current) setIsRefreshing(false);
    }
  }, [scanId, urlHint]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    loadScanDetail(scanId, urlHint).then(({ scan: s, source: src }) => {
      if (cancelled || !mounted.current) return;
      setScan(s);
      setSource(src);
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [scanId, urlHint]);

  const onLocalPageType = useCallback((pageType: string) => {
    setScan((prev) => (prev ? { ...prev, page_type_final: pageType } : prev));
  }, []);

  useEffect(() => {
    if (source !== "api" || !isScanStatusNonFinal(scan?.status)) {
      return;
    }
    const tick = () => {
      void (async () => {
        try {
          const s = await fetchScanDetailFromApi(scanId);
          if (!mounted.current) return;
          setScan(s);
        } catch {
          /* ignore transient errors while polling */
        }
      })();
    };
    const id = window.setInterval(tick, SCAN_POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [source, scan?.status, scanId]);

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

  const showPollingHint = source === "api" && scan && isScanStatusNonFinal(scan.status);

  return (
    <>
      {isRefreshing ? (
        <p className="small muted syncHint" role="status">
          Syncing with server…
        </p>
      ) : null}
      {showPollingHint ? (
        <p className="small muted syncHint" role="status">
          Analysis in progress — updating every few seconds.
        </p>
      ) : null}
      <ResultShell
        scan={scan}
        routeScanId={scanId}
        source={source}
        urlDisplay={urlDisplay}
        onLocalPageType={onLocalPageType}
        onRefetchScan={refetchScan}
      />
    </>
  );
}
