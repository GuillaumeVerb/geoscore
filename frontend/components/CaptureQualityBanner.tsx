/** Lightweight caution for shared reports when limitations indicate incomplete capture. */

type Props = { visible: boolean };

export function CaptureQualityBanner({ visible }: Props) {
  if (!visible) {
    return null;
  }

  return (
    <div className="statusBanner statusBanner--partial" role="status">
      <p className="statusBannerTitle">Limited capture</p>
      <p className="statusBannerBody">
        This shared snapshot may not reflect the full page. Review the limitations below before acting on
        scores or fixes.
      </p>
    </div>
  );
}
