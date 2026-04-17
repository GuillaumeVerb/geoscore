import type { Metadata } from "next";

import { LandingAnalyzeSection } from "@/components/landing/LandingAnalyzeSection";
import { LandingFooterCta } from "@/components/landing/LandingFooterCta";
import { LandingHero } from "@/components/landing/LandingHero";
import { LandingRepeatUseSection } from "@/components/landing/LandingRepeatUseSection";
import { LandingResultPreview } from "@/components/landing/LandingResultPreview";
import { LandingTrust } from "@/components/landing/LandingTrust";
import { LandingValuePillars } from "@/components/landing/LandingValuePillars";
import { LandingWhySeoGeo } from "@/components/landing/LandingWhySeoGeo";

export const metadata: Metadata = {
  title: {
    absolute: "GeoScore — SEO & GEO analyzer",
  },
  description:
    "Paste a URL. Get a serious SEO & GEO score. Understand whether a page is ready to rank, be understood, and be cited in modern search environments.",
};

export default function HomePage() {
  return (
    <main className="landing">
      <LandingHero />
      <LandingAnalyzeSection />
      <LandingValuePillars />
      <LandingWhySeoGeo />
      <LandingResultPreview />
      <LandingRepeatUseSection />
      <LandingTrust />
      <LandingFooterCta />
    </main>
  );
}
