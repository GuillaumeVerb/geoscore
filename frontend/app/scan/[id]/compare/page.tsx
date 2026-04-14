import type { Metadata } from "next";
import { Suspense } from "react";

import { ScanCompareView } from "@/components/ScanCompareView";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  return { title: "Compare scans", description: `Before/after comparison for scan ${id.slice(0, 8)}…` };
}

export default async function ScanComparePage({ params }: Props) {
  const { id } = await params;
  return (
    <Suspense
      fallback={
        <main className="resultMain" aria-busy="true">
          <p className="muted">Loading…</p>
        </main>
      }
    >
      <ScanCompareView scanId={id} />
    </Suspense>
  );
}
