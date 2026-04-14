"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { DashboardScanHistory } from "@/components/DashboardScanHistory";
import { isSignedIn } from "@/lib/authStorage";

export function DashboardGate() {
  const [ready, setReady] = useState(false);
  const [signedIn, setSignedIn] = useState(false);

  const sync = useCallback(() => {
    setSignedIn(isSignedIn());
    setReady(true);
  }, []);

  useEffect(() => {
    sync();
    window.addEventListener("geoscore-auth", sync);
    return () => window.removeEventListener("geoscore-auth", sync);
  }, [sync]);

  if (!ready) {
    return (
      <section className="dashState" aria-live="polite">
        <p className="muted">Loading…</p>
      </section>
    );
  }

  if (!signedIn) {
    return (
      <section className="card dashSignedOut" aria-labelledby="dash-signin-heading">
        <h2 className="h2" id="dash-signin-heading">
          Sign in to see your scans
        </h2>
        <p className="muted" style={{ marginBottom: "1rem", maxWidth: "34rem" }}>
          Recent analyses are private to your account. Sign in with your email to create scans and view your history.
        </p>
        <Link href="/sign-in?returnTo=/dashboard" className="button">
          Sign in
        </Link>
        {" · "}
        <Link href="/" className="small">
          Home
        </Link>
      </section>
    );
  }

  return <DashboardScanHistory />;
}
