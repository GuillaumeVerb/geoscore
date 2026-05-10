import type { Metadata } from "next";

import type { BlogPostMeta } from "@/lib/blogPosts";

export function blogPostMetadata(post: BlogPostMeta, description: string): Metadata {
  const path = `/blog/${post.slug}`;
  const publishedTime = `${post.date}T12:00:00.000Z`;
  const modifiedTime = `${post.updated ?? post.date}T12:00:00.000Z`;
  return {
    title: post.title,
    description,
    alternates: { canonical: path },
    openGraph: {
      type: "article",
      title: post.title,
      description,
      url: path,
      publishedTime,
      modifiedTime,
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description,
    },
  };
}
