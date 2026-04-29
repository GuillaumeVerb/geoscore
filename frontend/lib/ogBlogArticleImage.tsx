import { ImageResponse } from "next/og";

export const BLOG_OG_IMAGE_SIZE = { width: 1200, height: 630 } as const;

const ACCENT = "#0f766e";
const BG = "#111827";

function titleFontSize(title: string): number {
  const len = title.length;
  if (len > 110) return 30;
  if (len > 75) return 36;
  if (len > 45) return 42;
  return 48;
}

export function blogOgImageAlt(title: string): string {
  return `${title} · GeoScore blog`;
}

export function createBlogArticleOgImageResponse(title: string): ImageResponse {
  const fs = titleFontSize(title);
  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          justifyContent: "center",
          background: `linear-gradient(145deg, ${ACCENT} 0%, #0d5c56 42%, ${BG} 100%)`,
          padding: 64,
        }}
      >
        <div
          style={{
            fontSize: 22,
            fontWeight: 600,
            letterSpacing: "0.04em",
            textTransform: "uppercase",
            color: "rgba(255,255,255,0.75)",
            fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
            marginBottom: 20,
          }}
        >
          GeoScore · Blog
        </div>
        <div
          style={{
            fontSize: fs,
            fontWeight: 700,
            lineHeight: 1.2,
            color: "#fff",
            maxWidth: 1060,
            fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
            letterSpacing: "-0.02em",
          }}
        >
          {title}
        </div>
      </div>
    ),
    { ...BLOG_OG_IMAGE_SIZE },
  );
}
