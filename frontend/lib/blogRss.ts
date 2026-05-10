import { BLOG_POSTS, postRevisionDate } from "@/lib/blogPosts";

export const BLOG_RSS_DESCRIPTION =
  "Short, product-led notes on SEO, GEO, and single-page readiness — aligned with how GeoScore analyzes one URL.";

function escapeXml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

/** RSS 2.0 channel for public blog posts (sorted newest first). `base` = canonical origin (no trailing slash). */
export function buildBlogRssXml(base: string): string {
  const origin = base.replace(/\/$/, "");
  const blogUrl = `${origin}/blog`;
  const sorted = [...BLOG_POSTS].sort((a, b) => postRevisionDate(b).localeCompare(postRevisionDate(a)));

  const items = sorted
    .map((p) => {
      const link = `${origin}/blog/${p.slug}`;
      const stamp = postRevisionDate(p);
      const pub = new Date(`${stamp}T12:00:00.000Z`);
      const pubDate = pub.toUTCString();
      return `    <item>
      <title>${escapeXml(p.title)}</title>
      <link>${escapeXml(link)}</link>
      <guid isPermaLink="true">${escapeXml(link)}</guid>
      <pubDate>${pubDate}</pubDate>
      <description>${escapeXml(p.lede)}</description>
    </item>`;
    })
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>GeoScore blog</title>
    <link>${escapeXml(blogUrl)}</link>
    <description>${escapeXml(BLOG_RSS_DESCRIPTION)}</description>
    <language>en</language>
    <atom:link href="${escapeXml(`${origin}/blog/rss.xml`)}" rel="self" type="application/rss+xml" />
${items}
  </channel>
</rss>`;
}
