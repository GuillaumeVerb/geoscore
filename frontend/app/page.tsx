import { UrlSubmitForm } from "@/components/UrlSubmitForm";

export default function HomePage() {
  return (
    <main>
      <h1 className="homeTitle">Analyze one page</h1>
      <p className="lead muted homeLead">
        One URL, one flow, one clear score — GEO + SEO readiness without the bloat.
      </p>
      <UrlSubmitForm />
      <p className="small muted homeFootnote">
        If the API is offline, you&apos;ll still see a full placeholder result using demo data.
      </p>
    </main>
  );
}
