"""URL normalization for scan submission (pipeline-analysis.md — normalization step)."""

from urllib.parse import urlparse


def normalize_submitted_url(raw: str) -> tuple[str, str, str]:
    """Return (normalized_url, domain, path)."""
    url = raw.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    domain = parsed.netloc or ""
    path = parsed.path or "/"
    normalized = f"{parsed.scheme}://{domain}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    return normalized, domain, path
