import type { BlogPostMeta } from "@/lib/blogPosts";
import { getSiteOrigin } from "@/lib/siteUrl";

type Props = { variant: "index" } | { variant: "post"; post: BlogPostMeta };

export function BlogBreadcrumbJsonLd(props: Props) {
  const origin = getSiteOrigin();
  const homeItem = {
    "@type": "ListItem",
    position: 1,
    name: "Home",
    item: `${origin}/`,
  };
  const blogItem = {
    "@type": "ListItem",
    position: 2,
    name: "Blog",
    item: `${origin}/blog`,
  };

  const itemListElement =
    props.variant === "index"
      ? [homeItem, blogItem]
      : [
          homeItem,
          blogItem,
          {
            "@type": "ListItem",
            position: 3,
            name: props.post.title,
            item: `${origin}/blog/${props.post.slug}`,
          },
        ];

  const payload = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement,
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(payload) }}
    />
  );
}
