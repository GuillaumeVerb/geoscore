import { Suspense } from "react";

import { ScanResultView } from "@/components/ScanResultView";

type Props = { params: Promise<{ id: string }> };

export default async function ScanPage({ params }: Props) {
  const { id } = await params;
  return (
    <Suspense
      fallback={
        <main className="resultMain">
          <p className="muted">Loading…</p>
        </main>
      }
    >
      <ScanResultView scanId={id} />
    </Suspense>
  );
}
