import type { Metadata } from "next";
import Link from "next/link";

import { AuthNav } from "@/components/AuthNav";

import "./globals.css";

export const metadata: Metadata = {
  title: { default: "GeoScore", template: "%s · GeoScore" },
  description:
    "Paste a URL. Get a serious SEO & GEO score — explainable issues, prioritized fixes, and clear confidence.",
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
        </div>
      </body>
    </html>
  );
}
