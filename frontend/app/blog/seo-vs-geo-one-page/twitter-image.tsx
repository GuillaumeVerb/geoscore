import {
  BLOG_OG_IMAGE_SIZE,
  blogOgImageAlt,
  createBlogArticleOgImageResponse,
} from "@/lib/ogBlogArticleImage";
import { getBlogPostMeta } from "@/lib/blogPosts";

const POST = getBlogPostMeta("seo-vs-geo-one-page")!;

export const alt = blogOgImageAlt(POST.title);
export const size = BLOG_OG_IMAGE_SIZE;
export const contentType = "image/png";

export default function Image() {
  return createBlogArticleOgImageResponse(POST.title);
}
