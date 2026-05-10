import { NextResponse } from "next/server";

import { buildBlogRssXml } from "@/lib/blogRss";
import { resolveSiteOrigin } from "@/lib/siteUrl";

export async function GET() {
  const base = await resolveSiteOrigin();
  const xml = buildBlogRssXml(base);
  return new NextResponse(xml, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
    },
  });
}
