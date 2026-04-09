import { Suspense } from "react";

import { PublicReportView } from "@/components/PublicReportView";

type Props = { params: Promise<{ publicId: string }> };

export default async function PublicReportPage({ params }: Props) {
  const { publicId } = await params;
  return (
    <Suspense
      fallback={
        <main className="resultMain">
          <p className="muted">Loading…</p>
        </main>
      }
    >
      <PublicReportView publicId={publicId} />
    </Suspense>
  );
}
