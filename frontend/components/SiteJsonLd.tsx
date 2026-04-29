import { getSiteOrigin } from "@/lib/siteUrl";

const DEFAULT_DESCRIPTION =
  "Paste one URL. Get SEO and GEO scores, clear limits, and fixes you can share or export — a small utility, not a full SEO suite.";

export function SiteJsonLd() {
  const origin = getSiteOrigin();
  const payload = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": `${origin}/#organization`,
        name: "GeoScore",
        url: origin,
        description: DEFAULT_DESCRIPTION,
      },
      {
        "@type": "WebSite",
        "@id": `${origin}/#website`,
        name: "GeoScore",
        url: origin,
        inLanguage: "en",
        description: DEFAULT_DESCRIPTION,
        publisher: { "@id": `${origin}/#organization` },
      },
    ],
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(payload) }}
    />
  );
}
