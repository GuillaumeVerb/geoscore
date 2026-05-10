import type { MetadataRoute } from "next";

import { resolveSiteOrigin } from "@/lib/siteUrl";

export default async function robots(): Promise<MetadataRoute.Robots> {
  const base = await resolveSiteOrigin();
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: `${base}/sitemap.xml`,
  };
}
