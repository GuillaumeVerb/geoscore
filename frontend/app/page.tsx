import type { Metadata } from "next";

import { LandingFooterCta } from "@/components/landing/LandingFooterCta";
import { LandingPrimaryTool } from "@/components/landing/LandingPrimaryTool";
import { LandingRepeatUseSection } from "@/components/landing/LandingRepeatUseSection";
import { LandingResultPreview } from "@/components/landing/LandingResultPreview";
import { LandingScopeBoundary } from "@/components/landing/LandingScopeBoundary";
import { LandingTrust } from "@/components/landing/LandingTrust";
import { LandingUtilityWhy } from "@/components/landing/LandingUtilityWhy";

export const metadata: Metadata = {
  title: {
    absolute: "GeoScore — SEO & GEO analyzer",
  },
  description:
    "Paste one URL. Get SEO and GEO scores, limits, and fixes you can share or export — a small utility, not a full SEO suite.",
};

export default function HomePage() {
  return (
    <main className="landing">
      <LandingPrimaryTool />
      <LandingScopeBoundary />
      <LandingResultPreview />
      <LandingRepeatUseSection />
      <LandingUtilityWhy />
      <LandingTrust />
      <LandingFooterCta />
    </main>
  );
}
