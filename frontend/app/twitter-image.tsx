import { createOgImageResponse, OG_IMAGE_ALT, OG_IMAGE_SIZE } from "@/lib/ogOpenGraphImage";

export const alt = OG_IMAGE_ALT;
export const size = OG_IMAGE_SIZE;
export const contentType = "image/png";

export default function Image() {
  return createOgImageResponse();
}
