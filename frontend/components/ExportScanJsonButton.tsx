"use client";

import { buildMinimalScanExport } from "@/lib/scanPresentation";
import type { ScanStatus } from "@/types/scan";

type Props = {
  scanId: string;
  url: string;
  scan: ScanStatus;
  oneLiner?: string;
};

export function ExportScanJsonButton({ scanId, url, scan, oneLiner }: Props) {
  function download() {
    const payload = buildMinimalScanExport({ scanId, url, scan, oneLiner });
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `geoscore-scan-${scanId}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <button type="button" className="button secondary" onClick={download} title="Minimal JSON for CI or Notion">
      Download report JSON
    </button>
  );
}
