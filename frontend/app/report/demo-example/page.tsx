import type { Metadata } from "next";
import { Suspense } from "react";

import { PublicReportView } from "@/components/PublicReportView";

export const metadata: Metadata = {
  title: "Example report",
  description:
    "Sample GeoScore shared report: global, SEO, and GEO scores, confidence, strengths, prioritized issues and fixes — same shape as a live public report.",
};

export default function DemoExampleReportPage() {
  return (
    <Suspense
      fallback={
        <main className="resultMain" aria-busy="true" aria-label="Example report">
          <p className="muted" role="status" aria-live="polite">
            Loading example report…
          </p>
        </main>
      }
    >
      <PublicReportView publicId="demo-example" presentation="exampleDemo" />
    </Suspense>
  );
}
