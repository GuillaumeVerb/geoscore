"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { clearAuthSession, getStoredUser, isSignedIn } from "@/lib/authStorage";

export function AuthNav() {
  const [signedIn, setSignedIn] = useState(false);
  const [email, setEmail] = useState<string | null>(null);

  const sync = useCallback(() => {
    setSignedIn(isSignedIn());
    setEmail(getStoredUser()?.email ?? null);
  }, []);

  useEffect(() => {
    sync();
    window.addEventListener("geoscore-auth", sync);
    return () => window.removeEventListener("geoscore-auth", sync);
  }, [sync]);

  function signOut() {
    clearAuthSession();
    sync();
  }

  if (!signedIn) {
    return (
      <Link href="/sign-in" className="navLink">
        Sign in
      </Link>
    );
  }

  return (
    <span className="navAccountWrap">
      <span className="navAccountEmail muted small" title={email ?? undefined}>
        {email ? email.split("@")[0] : "Account"}
      </span>
      <button type="button" className="navSignOut" onClick={signOut}>
        Sign out
      </button>
    </span>
  );
}
