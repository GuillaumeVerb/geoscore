import type { Metadata } from "next";

export const metadata: Metadata = {
  alternates: {
    types: {
      "application/rss+xml": [{ url: "/blog/rss.xml", title: "GeoScore blog" }],
    },
  },
};

export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return children;
}
