import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "GeoScore",
  description: "Minimal SEO & GEO analyzer",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <nav className="nav" aria-label="Main">
            <Link href="/" className="brand">
              GeoScore
            </Link>
            <Link href="/dashboard">Dashboard</Link>
            <Link href="/pricing">Pricing</Link>
          </nav>
          {children}
        </div>
      </body>
    </html>
  );
}
