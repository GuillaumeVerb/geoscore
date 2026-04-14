import { Suspense } from "react";

import { ScanResultView } from "@/components/ScanResultView";

type Props = { params: Promise<{ id: string }> };

export default async function ScanPage({ params }: Props) {
  const { id } = await params;
  return (
    <Suspense
      fallback={
        <main className="resultMain" aria-busy="true" aria-label="Scan result">
          <p className="muted" role="status" aria-live="polite">
            Loading scan…
          </p>
        </main>
      }
    >
      <ScanResultView scanId={id} />
    </Suspense>
  );
}
