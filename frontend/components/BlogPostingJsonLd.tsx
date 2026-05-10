import type { BlogPostMeta } from "@/lib/blogPosts";
import { getSiteOrigin } from "@/lib/siteUrl";

type Props = {
  post: BlogPostMeta;
  description: string;
};

export function BlogPostingJsonLd({ post, description }: Props) {
  const origin = getSiteOrigin();
  const url = `${origin}/blog/${post.slug}`;
  const blogUrl = `${origin}/blog`;

  const payload = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "@id": `${url}#article`,
    headline: post.title,
    description,
    datePublished: post.date,
    dateModified: post.updated ?? post.date,
    url,
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": url,
    },
    author: {
      "@type": "Organization",
      name: "GeoScore",
      url: origin,
      description: "GeoScore builds a minimal SEO and GEO analyzer for single public URLs.",
    },
    publisher: {
      "@type": "Organization",
      name: "GeoScore",
      url: origin,
      description: "GeoScore builds a minimal SEO and GEO analyzer for single public URLs.",
    },
    isPartOf: {
      "@type": "Blog",
      "@id": `${blogUrl}#blog`,
      name: "GeoScore blog",
      url: blogUrl,
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(payload) }}
    />
  );
}
