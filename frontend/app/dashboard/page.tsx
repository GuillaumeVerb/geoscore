import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { DashboardGate } from "@/components/DashboardGate";

export const metadata: Metadata = {
  title: "Recent scans",
  description: "Your recent GeoScore analyses: status, scores, and quick links back to each result.",
  robots: { index: false, follow: true },
};

export default function DashboardPage() {
  return (
    <main className="resultMain dashPage">
      <header className="dashPageHeader">
        <h1 className="resultTitle">Recent scans</h1>
        <p className="muted dashPageLead">
          A simple history of URLs you&apos;ve analyzed. Optional projects let you group and filter by client or site.
          Open any row for the full result — scores, issues, and fixes stay on the result page.
        </p>
        <p className="dashPageNav">
          <Link href="/#analyze" className="button secondary">
            Analyze a URL
          </Link>
          <Link href="/" className="small muted dashPageNavLink">
            Home
          </Link>
        </p>
      </header>

      <Suspense
        fallback={
          <section className="dashState" aria-live="polite">
            <p className="muted">Loading dashboard…</p>
          </section>
        }
      >
        <DashboardGate />
      </Suspense>
    </main>
  );
}
