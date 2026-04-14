"use client";

import Link from "next/link";

import { UrlSubmitForm } from "@/components/UrlSubmitForm";

export function LandingAnalyzeSection() {
  return (
    <section className="landingSection landingAnalyze" id="analyze" aria-labelledby="analyze-heading">
      <h2 className="landingSectionTitle" id="analyze-heading">
        Analyze a page
      </h2>
      <p className="landingSectionLead">
        Paste a public URL. You&apos;ll get scores, issues, and prioritized fixes in one flow.
      </p>
      <div className="landingInputCard">
        <UrlSubmitForm submitButtonText="Analyze a URL" />
        <p className="small muted landingInputHint">
          Works best with live pages. If the analyzer can&apos;t be reached, you&apos;ll see a full demo result instead.
        </p>
        <p className="small muted landingInputHint" style={{ marginTop: "0.35rem" }}>
          <Link href="/dashboard">Recent scans</Link>
          <span aria-hidden="true"> · </span>
          <Link href="/report/demo-example">Example report</Link>
        </p>
      </div>
    </section>
  );
}
