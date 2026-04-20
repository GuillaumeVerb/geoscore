/**
 * Canonical site origin for sitemap and robots (server-side only).
 * Set NEXT_PUBLIC_SITE_URL in production (https://…, no trailing slash).
 * On Vercel, VERCEL_URL is injected when unset — previews use the deployment host.
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
