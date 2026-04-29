import { loadPublicReport } from "@/lib/loadScan";
import {
  createPublicReportOgImageResponse,
  REPORT_OG_IMAGE_SIZE,
} from "@/lib/ogPublicReportImage";

export const alt = "GeoScore shared report";
export const size = REPORT_OG_IMAGE_SIZE;
export const contentType = "image/png";

type Props = { params: Promise<{ publicId: string }> };

export default async function Image({ params }: Props) {
  const { publicId } = await params;
  const { report } = await loadPublicReport(publicId);
  return createPublicReportOgImageResponse(report);
}
