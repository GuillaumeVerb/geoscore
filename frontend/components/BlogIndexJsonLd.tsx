import { BLOG_POSTS } from "@/lib/blogPosts";
import { getSiteOrigin } from "@/lib/siteUrl";

export function BlogIndexJsonLd() {
  const origin = getSiteOrigin();
  const blogUrl = `${origin}/blog`;

  const blogPost = BLOG_POSTS.map((p) => ({
    "@type": "BlogPosting",
    headline: p.title,
    url: `${origin}/blog/${p.slug}`,
    datePublished: p.date,
    dateModified: p.updated ?? p.date,
    description: p.lede,
  }));

  const payload = {
    "@context": "https://schema.org",
    "@type": "Blog",
    "@id": `${blogUrl}#blog`,
    name: "GeoScore blog",
    url: blogUrl,
    description:
      "Short, product-led notes on SEO, GEO, and single-page readiness — aligned with how GeoScore analyzes one URL.",
    publisher: {
      "@type": "Organization",
      name: "GeoScore",
      url: origin,
    },
    blogPost,
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(payload) }}
    />
  );
}
