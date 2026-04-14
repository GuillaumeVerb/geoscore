import type { Metadata } from "next";
import { Suspense } from "react";

export const metadata: Metadata = {
  title: "Sign in",
  description: "Sign in to GeoScore with your email to save scans and view your private history.",
};

export default function SignInLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense
      fallback={
        <main className="resultMain">
          <p className="muted">Loading…</p>
        </main>
      }
    >
      {children}
    </Suspense>
  );
}
