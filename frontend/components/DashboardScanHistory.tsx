"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { UrlSubmitForm } from "@/components/UrlSubmitForm";
import { ApiError, getJson, postJson } from "@/lib/api";
import { isInProgressStatus, statusLabel } from "@/lib/scanPresentation";
import type { ProjectRead } from "@/types/project";
import type { ScanSummary } from "@/types/scan";

type ListResponse = { scans: ScanSummary[] };

function formatScore(v: number | null | undefined) {
  if (v === null || v === undefined) return "—";
  return String(Math.round(v));
}

function formatWhen(iso: string | null | undefined) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function pageTypeLabel(s: ScanSummary) {
  return s.page_type_final ?? s.page_type_detected ?? null;
}

function statusPillClass(status: string) {
  const st = status.toLowerCase();
  if (st === "completed") return "dashPill dashPill--completed";
  if (st === "partial") return "dashPill dashPill--partial";
  if (st === "failed") return "dashPill dashPill--failed";
  if (isInProgressStatus(status)) return "dashPill dashPill--progress";
  return "dashPill";
}

function rowToneClass(status: string) {
  const st = status.toLowerCase();
  if (st === "partial") return "dashRow dashRow--partial";
  if (st === "failed") return "dashRow dashRow--failed";
  if (isInProgressStatus(status)) return "dashRow dashRow--progress";
  return "dashRow";
}

function ScanRow({ scan }: { scan: ScanSummary }) {
  const pt = pageTypeLabel(scan);
  const conf = scan.analysis_confidence ?? "—";
  const title = scan.domain || scan.submitted_url;
  const showCompare = Boolean(scan.parent_scan_id) && !isInProgressStatus(scan.status);

  return (
    <article className={rowToneClass(scan.status)}>
      <div className="dashRowTop">
        <div className="dashRowTitleBlock">
          <h3 className="dashRowTitle">
            <Link href={`/scan/${scan.scan_id}`} className="dashRowLink">
              {title}
            </Link>
          </h3>
          <p className="mono small muted dashRowUrl">{scan.submitted_url}</p>
        </div>
        <span className={statusPillClass(scan.status)}>{statusLabel(scan.status)}</span>
      </div>
      {scan.status.toLowerCase() === "partial" ? (
        <p className="small muted dashRowNote">Analysis finished with limitations — open the result for full context.</p>
      ) : null}
      {scan.status.toLowerCase() === "failed" ? (
        <p className="small muted dashRowNote">This run did not complete — open for details or try again from the result page.</p>
      ) : null}
      <dl className="dashRowMeta">
        <div>
          <dt>Global</dt>
          <dd>{formatScore(scan.global_score)}</dd>
        </div>
        <div>
          <dt>SEO</dt>
          <dd>{formatScore(scan.seo_score)}</dd>
        </div>
        <div>
          <dt>GEO</dt>
          <dd>{formatScore(scan.geo_score)}</dd>
        </div>
        <div>
          <dt>Page type</dt>
          <dd className="mono">{pt ?? "—"}</dd>
        </div>
        <div>
          <dt>Confidence</dt>
          <dd className="mono">{conf}</dd>
        </div>
        <div>
          <dt>Started</dt>
          <dd>{formatWhen(scan.created_at)}</dd>
        </div>
      </dl>
      <p className="dashRowAction">
        <Link
          href={`/scan/${scan.scan_id}`}
          className="button secondary small"
          aria-label={`Open scan result for ${title}`}
        >
          Open result
        </Link>
        {showCompare ? (
          <Link
            href={`/scan/${scan.scan_id}/compare`}
            className="button secondary small"
            title="Compare to previous run"
            aria-label={`Compare to previous run for ${title}`}
          >
            Compare to previous run
          </Link>
        ) : null}
      </p>
    </article>
  );
}

type ToolbarProps = {
  projects: ProjectRead[];
  /** Value for the filter &lt;select&gt; (empty string = all scans). */
  filterSelectValue: string;
  newProjectName: string;
  setNewProjectName: (v: string) => void;
  onSelectProject: (id: string | null) => void;
  onCreateProject: (e: React.FormEvent) => void;
  creating: boolean;
  createError: string | null;
  loading: boolean;
  submitScanButtonText: string;
  activeProjectId: string | null;
};

function ProjectToolbar({
  projects,
  filterSelectValue,
  newProjectName,
  setNewProjectName,
  onSelectProject,
  onCreateProject,
  creating,
  createError,
  loading,
  submitScanButtonText,
  activeProjectId,
}: ToolbarProps) {
  return (
    <section className="card block dashProjectToolbar" aria-labelledby="dash-project-heading">
      <h2 className="h2" id="dash-project-heading">
        Project &amp; new scan
      </h2>
      <p className="small muted sectionLead">
        Group scans by client or site. New analyses below attach to the project you select (optional).
      </p>
      <div className="dashProjectToolbarRow">
        <label htmlFor="dash-project-select">
          <span className="muted">Filter history</span>
          <select
            id="dash-project-select"
            value={filterSelectValue}
            disabled={loading}
            onChange={(e) => onSelectProject(e.target.value || null)}
            aria-busy={loading}
          >
            <option value="">All scans</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
        <form className="row" onSubmit={onCreateProject} style={{ flexWrap: "wrap", gap: "0.5rem" }}>
          <label htmlFor="dash-new-project" style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            <span className="muted small">New project</span>
            <input
              id="dash-new-project"
              type="text"
              className="input"
              placeholder="e.g. Client — homepage"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              maxLength={200}
              disabled={loading || creating}
              style={{ minWidth: "12rem" }}
            />
          </label>
          <button
            type="submit"
            className="button secondary"
            disabled={loading || creating || !newProjectName.trim()}
          >
            {creating ? "…" : "Create"}
          </button>
        </form>
      </div>
      {createError ? (
        <p className="error small" role="alert" style={{ marginTop: "0.5rem" }}>
          {createError}
        </p>
      ) : null}
      <UrlSubmitForm submitButtonText={submitScanButtonText} projectId={activeProjectId} />
    </section>
  );
}

export function DashboardScanHistory() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectFromUrl = searchParams.get("project");
  const selectedProjectId = useMemo(() => {
    if (!projectFromUrl || !/^[0-9a-f-]{36}$/i.test(projectFromUrl)) return null;
    return projectFromUrl;
  }, [projectFromUrl]);

  const [scans, setScans] = useState<ScanSummary[] | null>(null);
  const [projects, setProjects] = useState<ProjectRead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [newProjectName, setNewProjectName] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const sanitizedBadUrl = useRef(false);

  /** UUID in query that is not in the loaded project list (stale bookmark or foreign id). */
  const unknownProjectFilter = Boolean(
    selectedProjectId &&
      !loading &&
      !error &&
      !projects.some((p) => p.id.toLowerCase() === selectedProjectId.toLowerCase()),
  );
  const filterSelectValue =
    selectedProjectId && projects.some((p) => p.id.toLowerCase() === selectedProjectId.toLowerCase())
      ? selectedProjectId
      : "";
  const activeProjectForSubmit = unknownProjectFilter ? null : selectedProjectId;
  const submitScanLabel = activeProjectForSubmit ? "Analyze in project" : "New scan";

  useEffect(() => {
    if (!projectFromUrl) {
      sanitizedBadUrl.current = false;
      return;
    }
    if (selectedProjectId) return;
    if (sanitizedBadUrl.current) return;
    sanitizedBadUrl.current = true;
    router.replace("/dashboard");
  }, [projectFromUrl, selectedProjectId, router]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [projRes, scanData] = await Promise.all([
        getJson<{ projects: ProjectRead[] }>("/api/projects"),
        getJson<ListResponse>(
          selectedProjectId
            ? `/api/scans?limit=50&project_id=${encodeURIComponent(selectedProjectId)}`
            : "/api/scans?limit=50",
        ),
      ]);
      setProjects(projRes.projects ?? []);
      setScans(scanData.scans ?? []);
    } catch (e) {
      setScans(null);
      setProjects([]);
      const msg =
        e instanceof ApiError
          ? e.message
          : e instanceof Error
            ? e.message
            : "Could not load scans.";
      const unauthorized =
        (e instanceof ApiError && e.status === 401) ||
        /\b401\b/i.test(msg) ||
        msg.toLowerCase().includes("not authenticated");
      setError(
        unauthorized
          ? "Session missing or expired. Sign in again to load your scan history."
          : msg,
      );
    } finally {
      setLoading(false);
    }
  }, [selectedProjectId]);

  useEffect(() => {
    void load();
  }, [load]);

  function onSelectProject(id: string | null) {
    if (id) router.replace(`/dashboard?project=${encodeURIComponent(id)}`);
    else router.replace("/dashboard");
  }

  async function onCreateProject(e: React.FormEvent) {
    e.preventDefault();
    const name = newProjectName.trim();
    if (!name) return;
    setCreating(true);
    setCreateError(null);
    try {
      const p = await postJson<ProjectRead>("/api/projects", { name });
      setNewProjectName("");
      router.replace(`/dashboard?project=${encodeURIComponent(p.id)}`);
    } catch (err) {
      const msg =
        err instanceof ApiError && err.status === 401
          ? "Session missing or expired. Sign in again to create a project."
          : err instanceof Error
            ? err.message
            : "Could not create project.";
      setCreateError(msg);
    } finally {
      setCreating(false);
    }
  }

  const toolbar = (
    <ProjectToolbar
      projects={projects}
      filterSelectValue={filterSelectValue}
      newProjectName={newProjectName}
      setNewProjectName={setNewProjectName}
      onSelectProject={onSelectProject}
      onCreateProject={(ev) => void onCreateProject(ev)}
      creating={creating}
      createError={createError}
      loading={loading}
      submitScanButtonText={submitScanLabel}
      activeProjectId={activeProjectForSubmit}
    />
  );

  const unknownProjectBanner =
    unknownProjectFilter && selectedProjectId ? (
      <div className="compareNotice" role="status" aria-live="polite">
        <p>
          This project is not in your list (it may have been removed or the link is wrong). Showing all scans until you
          pick a filter.
        </p>
        <div className="row">
          <button type="button" className="button secondary small" onClick={() => onSelectProject(null)}>
            Clear filter
          </button>
        </div>
      </div>
    ) : null;

  if (loading) {
    return (
      <div className="dashListWrap">
        {toolbar}
        <section className="dashState" aria-busy="true" aria-label="Scan history">
          <p className="muted" role="status" aria-live="polite">
            Loading recent scans…
          </p>
        </section>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashListWrap">
        {toolbar}
        <section className="dashState card" role="alert" aria-live="assertive">
          <h2 className="h2">Couldn&apos;t load history</h2>
          <p className="muted small" style={{ marginBottom: "0.75rem" }}>
            {error} Check that the backend is running and <span className="mono">NEXT_PUBLIC_API_URL</span> points to it
          (see README).
          </p>
          <div className="row">
            <button type="button" className="button secondary" onClick={() => void load()} aria-label="Retry loading scan history">
              Retry
            </button>
            <Link href="/sign-in?returnTo=%2Fdashboard" className="button secondary">
              Sign in
            </Link>
            <Link href="/" className="button">
              Analyze a URL
            </Link>
          </div>
        </section>
      </div>
    );
  }

  const list = scans ?? [];
  if (!list.length) {
    return (
      <div className="dashListWrap">
        {toolbar}
        {unknownProjectBanner}
        <section className="dashEmpty card" aria-labelledby="dash-empty-heading" role="status" aria-live="polite">
          <h2 className="h2" id="dash-empty-heading">
            {unknownProjectFilter
              ? "Nothing to show for this link"
              : filterSelectValue
                ? "No scans in this project"
                : "No scans yet"}
          </h2>
          <p className="muted" style={{ marginBottom: "1rem", maxWidth: "34rem" }}>
            {filterSelectValue
              ? "Run an analysis with the project selected above, or pick another project from the filter."
              : "When you analyze URLs, they show up here with status and scores. After you change the page, use Rescan on a result, then open Compare to previous run to see what moved — still one URL at a time."}
          </p>
          {filterSelectValue ? (
            <button type="button" className="button secondary" onClick={() => onSelectProject(null)}>
              Show all scans
            </button>
          ) : (
            <Link href="/#analyze" className="button">
              Analyze a URL
            </Link>
          )}
        </section>
      </div>
    );
  }

  const inProgress = list.filter((s) => isInProgressStatus(s.status));
  const settled = list.filter((s) => !isInProgressStatus(s.status));

  return (
    <div className="dashListWrap">
      {toolbar}
      {unknownProjectBanner}

      {inProgress.length > 0 ? (
        <section className="dashGroup" aria-labelledby="dash-inprog-heading">
          <h2 className="dashGroupTitle" id="dash-inprog-heading">
            In progress
          </h2>
          <p className="small muted dashGroupHint">These scans are still running through the pipeline.</p>
          <div className="dashList">
            {inProgress.map((s) => (
              <ScanRow key={s.scan_id} scan={s} />
            ))}
          </div>
        </section>
      ) : null}

      <section className="dashGroup" aria-labelledby="dash-recent-heading">
        <h2 className="dashGroupTitle" id="dash-recent-heading">
          {inProgress.length > 0 ? "Recent scans" : "All scans"}
        </h2>
        {settled.length === 0 ? (
          <p className="muted small">No completed or final scans yet.</p>
        ) : (
          <div className="dashList">
            {settled.map((s) => (
              <ScanRow key={s.scan_id} scan={s} />
            ))}
          </div>
        )}
      </section>

      <p className="dashFooter muted small">
        <Link href="/#analyze">+ New analysis</Link>
        {" · "}
        <Link href="/report/demo-example">Example report</Link>
      </p>
    </div>
  );
}
