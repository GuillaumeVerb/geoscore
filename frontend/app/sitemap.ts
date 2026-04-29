import type { MetadataRoute } from "next";

import { BLOG_POSTS } from "@/lib/blogPosts";
import { getSiteOrigin } from "@/lib/siteUrl";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = getSiteOrigin();

  const staticPages: MetadataRoute.Sitemap = [
    { url: `${base}/`, lastModified: new Date(), changeFrequency: "weekly", priority: 1 },
    { url: `${base}/how-it-works`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.85 },
    { url: `${base}/pricing`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.75 },
    { url: `${base}/blog`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
    {
      url: `${base}/report/demo-example`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.7,
    },
    { url: `${base}/privacy`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.4 },
  ];

  const blogPages: MetadataRoute.Sitemap = BLOG_POSTS.map((p) => ({
    url: `${base}/blog/${p.slug}`,
    lastModified: new Date(p.date),
    changeFrequency: "monthly" as const,
    priority: 0.65,
  }));

  return [...staticPages, ...blogPages];
}
