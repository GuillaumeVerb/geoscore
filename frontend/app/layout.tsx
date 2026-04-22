import type { Metadata } from "next";
import Link from "next/link";

import { AuthNav } from "@/components/AuthNav";
import { SiteFooter } from "@/components/SiteFooter";

import "./globals.css";

export const metadata: Metadata = {
  title: { default: "GeoScore", template: "%s · GeoScore" },
  description:
    "Paste one URL. Get SEO and GEO scores, clear limits, and fixes you can share or export — a small utility, not a full SEO suite.",
  /** Google Search Console — URL prefix property (HTML tag method). Override via env if the token rotates. */
  verification: {
    google:
      process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION?.trim() ||
      "2mLCmOGDw6WCtYQ9-Bco0WZHTFJfOoh2zrEH8hPDb74",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <a href="#main-content" className="skipLink">
            Skip to main content
          </a>
          <nav className="nav" aria-label="Main">
            <Link href="/" className="brand">
              GeoScore
            </Link>
            <Link href="/dashboard" className="navLink">
              Recent scans
            </Link>
            <Link href="/pricing" className="navLink">
              Pricing
            </Link>
            <Link href="/how-it-works" className="navLink">
              How scoring works
            </Link>
            <Link href="/blog" className="navLink">
              Blog
            </Link>
            <span className="navAuth">
              <AuthNav />
            </span>
          </nav>
          <div id="main-content" tabIndex={-1} className="mainContent">
            {children}
          </div>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
