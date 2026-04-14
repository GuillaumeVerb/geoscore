import { statusLabel } from "@/lib/scanPresentation";

type Props = {
  status: string | undefined;
  errorCode?: string | null;
  errorMessage?: string | null;
};

export function ScanStatusBanner({ status, errorCode, errorMessage }: Props) {
  const s = (status ?? "").toLowerCase();

  if (s === "completed") {
    return null;
  }

  if (s === "failed") {
    const msg = (errorMessage ?? "").trim() || "This scan did not finish successfully.";
    const short = msg.length > 320 ? `${msg.slice(0, 320)}…` : msg;
    return (
      <div className="statusBanner statusBanner--failed" role="alert">
        <p className="statusBannerTitle">Analysis did not complete</p>
        <p className="statusBannerBody">{short}</p>
        {errorCode ? (
          <p className="small muted" style={{ marginTop: "0.35rem", marginBottom: 0 }}>
            Reference: <span className="mono">{errorCode}</span>
          </p>
        ) : null}
      </div>
    );
  }

  if (s === "partial") {
    return (
      <div className="statusBanner statusBanner--partial" role="status">
        <p className="statusBannerTitle">{statusLabel(status)}</p>
        <p className="statusBannerBody">
          Scores and issues may reflect an incomplete capture. Review limitations and capture-related notes
          before prioritizing fixes.
        </p>
      </div>
    );
  }

  return null;
}
