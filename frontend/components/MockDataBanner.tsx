type Props = { message?: string };

export function MockDataBanner({ message = "Showing demo data — API unreachable or preview mode." }: Props) {
  return (
    <div className="mockBanner" role="status">
      <span className="mockBannerLabel">Demo</span>
      <span>{message}</span>
    </div>
  );
}
