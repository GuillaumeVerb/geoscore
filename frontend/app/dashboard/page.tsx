import Link from "next/link";

export default function DashboardPage() {
  return (
    <main className="resultMain">
      <h1 className="resultTitle">Dashboard</h1>
      <p className="muted">
        Scan history and projects will appear here once the backend persists runs and auth is wired.
      </p>
      <section className="card block" style={{ marginTop: "1rem" }}>
        <h2 className="h2">Placeholder</h2>
        <p className="muted small" style={{ marginBottom: "0.75rem" }}>
          No saved scans yet. Start from the home page or open a demo result.
        </p>
        <Link href="/" className="small">
          ← Home
        </Link>
        {" · "}
        <Link href="/scan/preview" className="small">
          Demo result (preview)
        </Link>
      </section>
    </main>
  );
}
