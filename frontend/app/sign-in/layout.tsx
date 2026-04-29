import type { Metadata } from "next";
import { Suspense } from "react";

export const metadata: Metadata = {
  robots: { index: false, follow: true },
};

export default function SignInLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense
      fallback={
        <main className="resultMain" aria-busy="true" aria-label="Sign in">
          <p className="muted" role="status">
            Loading…
          </p>
        </main>
      }
    >
      {children}
    </Suspense>
  );
}
