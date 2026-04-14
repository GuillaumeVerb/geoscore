"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { postJson } from "@/lib/api";
import { setAuthSession } from "@/lib/authStorage";

type SessionResponse = {
  access_token: string;
  token_type: string;
  user: { id: string; email: string };
};

export default function SignInPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const returnTo = (() => {
    const raw = searchParams.get("returnTo");
    if (!raw || !raw.startsWith("/") || raw.startsWith("//")) return "/dashboard";
    return raw;
  })();

  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await postJson<SessionResponse>("/api/auth/session", { email: email.trim() });
      setAuthSession(data.access_token, { id: String(data.user.id), email: data.user.email });
      if (returnTo.includes("#")) {
        window.location.assign(returnTo);
      } else {
        router.push(returnTo);
        router.refresh();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not sign in. Try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="resultMain">
      <h1 className="resultTitle">Sign in</h1>
      <p className="muted" style={{ maxWidth: "32rem", marginBottom: "1.25rem" }}>
        Enter your email to continue. GeoScore uses a simple browser session (no magic link in your inbox yet). Use
        the same email on each device to see the same history. Your scan list stays private to that email.
      </p>

      <form onSubmit={onSubmit} className="card stack" style={{ maxWidth: "22rem" }} aria-busy={loading}>
        <label className="label" htmlFor="signin-email">
          Email
        </label>
        <input
          id="signin-email"
          name="email"
          type="email"
          required
          autoComplete="email"
          className="input"
          style={{ width: "100%" }}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        {error ? (
          <p className="error" role="alert">
            {error}
          </p>
        ) : null}
        <button type="submit" className="button" disabled={loading}>
          {loading ? "…" : "Continue"}
        </button>
      </form>

      <p className="small muted" style={{ marginTop: "1.25rem" }}>
        <Link href="/">← Home</Link>
        {" · "}
        <Link href="/how-it-works">How scoring works</Link>
        {" · "}
        <Link href="/report/demo-example">Example report</Link>
      </p>
    </main>
  );
}
