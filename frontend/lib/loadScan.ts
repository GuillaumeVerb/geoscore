import { getJson } from "@/lib/api";
import { buildMockPublicReport, buildMockScanDetail, PREVIEW_SCAN_ID } from "@/lib/mockData";
import type { PublicReport, ScanStatus } from "@/types/scan";

export type DataSource = "api" | "mock";

export async function loadScanDetail(
  scanId: string,
  urlHint?: string,
): Promise<{ scan: ScanStatus; source: DataSource }> {
  if (scanId === PREVIEW_SCAN_ID) {
    return { scan: buildMockScanDetail(scanId, urlHint), source: "mock" };
  }
  try {
    const scan = await getJson<ScanStatus>(`/api/scans/${scanId}`);
    return { scan, source: "api" };
  } catch {
    return { scan: buildMockScanDetail(scanId, urlHint), source: "mock" };
  }
}

export async function loadPublicReport(
  publicId: string,
  urlHint?: string,
): Promise<{ report: PublicReport; source: DataSource }> {
  try {
    const report = await getJson<PublicReport>(`/api/public-reports/${publicId}`);
    return { report, source: "api" };
  } catch {
    return { report: buildMockPublicReport(publicId, urlHint), source: "mock" };
  }
}
