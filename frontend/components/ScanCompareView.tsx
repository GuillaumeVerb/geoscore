"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { ApiError, getJson } from "@/lib/api";
import type { ScanIssue, ScanRecommendation } from "@/types/scan";

type CompareScores = { global_score?: number | null; seo_score?: number | null; geo_score?: number | null };

type ComparePayload = {
  parent_scan_id: string;
  child_scan_id: string;
  submitted_url: string;
  before_scores: CompareScores;
  after_scores: CompareScores;
  resolved_issues: ScanIssue[];
  new_issues: ScanIssue[];
  recommendations_persistent: ScanRecommendation[];
  recommendations_new: ScanRecommendation[];
  recommendations_removed: ScanRecommendation[];
};

function fmt(n: number | null | undefined) {
  if (n === null || n === undefined) return "—";
  return String(Math.round(n));
}

function delta(b: number | null | undefined, a: number | null | undefined): string {
  if (b === null || b === undefined || a === null || a === undefined) return "—";
  const d = Math.round(a) - Math.round(b);
  if (d === 0) return "0";
  return d > 0 ? `+${d}` : String(d);
}

function deltaToneClass(d: string): string {
  if (d === "—") return "mono";
  if (d === "0") return "mono compareDelta--flat";
  if (d.startsWith("+")) return "mono compareDelta--up";
  return "mono compareDelta--down";
}

function shortUuid(id: string) {
  if (!id || id.length < 8) return id || "—";
  return `${id.slice(0, 8)}…`;
}

function CompareScoreRow({
  label,
  before: bv,
  after: av,
}: {
  label: string;
  before: number | null | undefined;
  after: number | null | undefined;
}) {
  const d = delta(bv, av);
  return (
    <tr>
      <th scope="row">{label}</th>
      <td>{fmt(bv)}</td>
      <td>{fmt(av)}</td>
      <td className={deltaToneClass(d)}>{d}</td>
    </tr>
  );
}

export function ScanCompareView({ scanId }: { scanId: string }) {
  const pathname = usePathname();
  const [data, setData] = useState<ComparePayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [errorStatus, setErrorStatus] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setErrorStatus(null);
    getJson<ComparePayload>(`/api/scans/${scanId}/compare`)
      .then((d) => {
        if (!cancelled) {
          setData(d);
          setErrorStatus(null);
        }
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        if (e instanceof ApiError) {
          setErrorStatus(e.status);
          setError(e.message);
        } else {
          setErrorStatus(null);
          setError(e instanceof Error ? e.message : "Could not load comparison.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [scanId]);

  if (loading) {
    return (
      <main className="resultMain" aria-busy="true">
        <p className="muted" role="status" aria-live="polite">
          Loading comparison…
        </p>
      </main>
    );
  }

  if (error || !data) {
    const is401 = errorStatus === 401;
    const is404 = errorStatus === 404;
    const returnTo = encodeURIComponent(pathname || `/scan/${scanId}/compare`);
    return (
      <main className="resultMain">
        <h1 className="resultTitle">Compare scans</h1>
        <p className="error" role="alert">
          {error ?? "No comparison available."}
        </p>
        {is401 ? (
          <p className="muted small">
            <Link href={`/sign-in?returnTo=${returnTo}`} className="button secondary small">
              Sign in
            </Link>
            {" · "}
            <Link href="/dashboard">Dashboard</Link>
          </p>
        ) : (
          <p className="muted small">
            {is404
              ? "This view only works for the newer scan in a rescan pair (the run that has a previous scan). Open a rescan from the dashboard or the result page."
              : "Comparisons apply to a rescan: open the newer scan, then use Compare to previous run."}
          </p>
        )}
        <p className="dashFooter muted small">
          <Link href="/dashboard">Recent scans</Link>
          {" · "}
          <Link href={`/scan/${scanId}`}>This scan</Link>
        </p>
      </main>
    );
  }

  const { before_scores: b, after_scores: a } = data;
  const urlLine = data.submitted_url?.trim() ? data.submitted_url : null;

  return (
    <main className="resultMain">
      <nav className="resultNavCrumb muted" aria-label="Compare navigation">
        <Link href="/dashboard">Recent scans</Link>
        <span aria-hidden="true"> · </span>
        <Link href={`/scan/${data.parent_scan_id}`}>Previous run</Link>
        <span aria-hidden="true"> · </span>
        <Link href={`/scan/${data.child_scan_id}`}>Latest result</Link>
      </nav>

      <header className="resultHeader">
        <h1 className="resultTitle">Before / after</h1>
        <p className="mono small muted">
          Previous <span className="mono">{shortUuid(data.parent_scan_id)}</span>
          {" → "}
          latest <span className="mono">{shortUuid(data.child_scan_id)}</span>
        </p>
        {urlLine ? (
          <p className="small muted" style={{ wordBreak: "break-all" }}>
            {urlLine}
          </p>
        ) : (
          <p className="small muted">Same analyzed URL as the previous run (URL not repeated in payload).</p>
        )}
      </header>

      <section className="card block" aria-labelledby="cmp-scores">
        <h2 className="h2" id="cmp-scores">
          Scores
        </h2>
        <p className="small muted sectionLead">Numbers come from each run as stored; change is simple after − before (not a separate engine).</p>
        <table className="compareTable">
          <caption className="compareCaption">
            Global, SEO, and GEO scores: before (parent scan) vs after (this scan).
          </caption>
          <thead>
            <tr>
              <th scope="col" />
              <th scope="col">Before</th>
              <th scope="col">After</th>
              <th scope="col">Change</th>
            </tr>
          </thead>
          <tbody>
            <CompareScoreRow label="Global" before={b.global_score} after={a.global_score} />
            <CompareScoreRow label="SEO" before={b.seo_score} after={a.seo_score} />
            <CompareScoreRow label="GEO" before={b.geo_score} after={a.geo_score} />
          </tbody>
        </table>
      </section>

      <section className="card block" aria-labelledby="cmp-resolved">
        <h2 className="h2" id="cmp-resolved">
          Resolved issues ({data.resolved_issues.length})
        </h2>
        <p className="small muted sectionLead">Issue codes present before but not after.</p>
        {data.resolved_issues.length === 0 ? (
          <p className="muted small">None</p>
        ) : (
          <ul className="compareIssueList">
            {data.resolved_issues.map((i) => (
              <li key={i.code}>
                <span className="mono">{i.code}</span> — {i.title}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card block" aria-labelledby="cmp-new">
        <h2 className="h2" id="cmp-new">
          New issues ({data.new_issues.length})
        </h2>
        <p className="small muted sectionLead">Issue codes present after but not before.</p>
        {data.new_issues.length === 0 ? (
          <p className="muted small">None</p>
        ) : (
          <ul className="compareIssueList">
            {data.new_issues.map((i) => (
              <li key={i.code}>
                <span className="mono">{i.code}</span> — {i.title}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card block" aria-labelledby="cmp-recs">
        <h2 className="h2" id="cmp-recs">
          Recommendations
        </h2>
        <p className="small muted sectionLead">Matched by key (or title): still relevant, new, or dropped.</p>
        <h3 className="h3 small">Still relevant ({data.recommendations_persistent.length})</h3>
        {data.recommendations_persistent.length === 0 ? (
          <p className="muted small">None</p>
        ) : (
          <ul className="compareIssueList">
            {data.recommendations_persistent.map((r, idx) => (
              <li key={`p-${idx}-${r.title}`}>{r.title}</li>
            ))}
          </ul>
        )}
        <h3 className="h3 small" style={{ marginTop: "1rem" }}>
          New ({data.recommendations_new.length})
        </h3>
        {data.recommendations_new.length === 0 ? (
          <p className="muted small">None</p>
        ) : (
          <ul className="compareIssueList">
            {data.recommendations_new.map((r, idx) => (
              <li key={`n-${idx}-${r.title}`}>{r.title}</li>
            ))}
          </ul>
        )}
        <h3 className="h3 small" style={{ marginTop: "1rem" }}>
          Dropped ({data.recommendations_removed.length})
        </h3>
        {data.recommendations_removed.length === 0 ? (
          <p className="muted small">None</p>
        ) : (
          <ul className="compareIssueList">
            {data.recommendations_removed.map((r, idx) => (
              <li key={`d-${idx}-${r.title}`}>{r.title}</li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
