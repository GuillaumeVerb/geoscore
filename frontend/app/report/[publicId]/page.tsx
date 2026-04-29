import type { Metadata } from "next";
import { Suspense } from "react";

import { PublicReportView } from "@/components/PublicReportView";
import { buildSharedReportMetadata } from "@/lib/publicReportMetadata";

type Props = { params: Promise<{ publicId: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { publicId } = await params;
  return buildSharedReportMetadata(publicId);
}

export default async function PublicReportPage({ params }: Props) {
  const { publicId } = await params;
  return (
    <Suspense
      fallback={
        <main className="resultMain" aria-busy="true" aria-label="Shared report">
          <p className="muted" role="status" aria-live="polite">
            Loading shared report…
          </p>
        </main>
      }
    >
      <PublicReportView publicId={publicId} />
    </Suspense>
  );
}
