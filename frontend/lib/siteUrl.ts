/**
 * Canonical site origin for JSON-LD, RSS, and fallbacks (server-side).
 * Set NEXT_PUBLIC_SITE_URL in production to the exact origin of your Search Console property
 * (https://…, no trailing slash), including www vs apex if you use one canonical host.
 * When unset on Vercel, VERCEL_URL is used — often *.vercel.app, which does not match a custom domain.
 */
export function getSiteOrigin(): string {
  const fromEnv = process.env.NEXT_PUBLIC_SITE_URL?.trim().replace(/\/$/, "");
  if (fromEnv) return fromEnv;
  const vercel = process.env.VERCEL_URL?.trim();
  if (vercel) {
    const host = vercel.replace(/^https?:\/\//, "");
    return `https://${host}`;
  }
  return "http://localhost:3000";
}

/**
 * Origin for sitemap.xml and robots.txt: env wins if set; otherwise derive from the incoming request
 * Host (fixes custom domain vs VERCEL_URL when NEXT_PUBLIC_SITE_URL is missing).
 */
export async function resolveSiteOrigin(): Promise<string> {
  const fromEnv = process.env.NEXT_PUBLIC_SITE_URL?.trim().replace(/\/$/, "");
  if (fromEnv) return fromEnv;

  try {
    const { headers } = await import("next/headers");
    const h = await headers();
    const rawHost =
      h.get("x-forwarded-host")?.split(",")[0]?.trim() ?? h.get("host")?.trim();
    if (rawHost) {
      const protoHeader = h.get("x-forwarded-proto")?.split(",")[0]?.trim();
      const proto =
        protoHeader ??
        (rawHost.startsWith("localhost") || rawHost.startsWith("127.") ? "http" : "https");
      return `${proto}://${rawHost}`;
    }
  } catch {
    /* No request context (e.g. build-time evaluation). */
  }

  return getSiteOrigin();
}
