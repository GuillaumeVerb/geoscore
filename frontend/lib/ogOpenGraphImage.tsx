import { ImageResponse } from "next/og";

export const OG_IMAGE_SIZE = { width: 1200, height: 630 } as const;

export const OG_IMAGE_ALT = "GeoScore — SEO and GEO readiness for one URL";

const ACCENT = "#0f766e";
const BG = "#111827";

export function createOgImageResponse(): ImageResponse {
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
          padding: 72,
        }}
      >
        <div
          style={{
            fontSize: 76,
            fontWeight: 700,
            color: "#fff",
            letterSpacing: "-0.03em",
            fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
          }}
        >
          GeoScore
        </div>
        <div
          style={{
            marginTop: 20,
            fontSize: 30,
            lineHeight: 1.35,
            color: "rgba(255,255,255,0.9)",
            maxWidth: 920,
            fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
          }}
        >
          SEO and GEO readiness for one URL — explainable scores, clear limits.
        </div>
      </div>
    ),
    { ...OG_IMAGE_SIZE },
  );
}
