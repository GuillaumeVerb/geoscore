"""
Product-layer fallbacks after deterministic scoring (does not change score formulas).

When a scan is partial with strong limitations but almost no issues/recommendations,
adds a diagnostic issue and practical guidance so users are not left with an empty report.
"""

from __future__ import annotations

from typing import Any

from app.schemas.issue import Issue
from app.schemas.recommendation import Recommendation

# Limitations that mean capture/render was materially constrained
_STRONG_LIMITATION_CODES = frozenset(
    {
        "FETCH_DEGRADED",
        "PARTIAL_PIPELINE",
        "PLAYWRIGHT_FAILED",
        "PLAYWRIGHT_NO_GAIN",
    }
)

_ISSUE_CODE = "CAPTURE_QUALITY_DEGRADED"
_RECO_RETRY = "IMPROVE_CAPTURE_OR_RETRY"
_RECO_VISIBLE = "VISIBLE_CONTENT_MAY_BE_INCOMPLETE"


def _lim_codes(limitations: list[Any]) -> set[str]:
    codes: set[str] = set()
    for lim in limitations:
        c = getattr(lim, "code", None) if not isinstance(lim, dict) else lim.get("code")
        if c:
            codes.add(str(c))
    return codes


def _already_has_code(issues: list[Issue], code: str) -> bool:
    return any(getattr(i, "code", None) == code for i in issues)


def _already_has_reco_key(recs: list[Recommendation], key: str) -> bool:
    return any((r.key or "") == key for r in recs)


def enrich_score_bundle_for_degraded_capture(
    score_bundle: dict[str, Any],
    *,
    is_partial: bool,
    pipeline_context: dict[str, Any] | None = None,
) -> None:
    """
    Mutates score_bundle ``issues`` and ``recommendations`` in place.

    New catalog-style codes:
    - Issue: ``CAPTURE_QUALITY_DEGRADED``
    - Recommendation: ``IMPROVE_CAPTURE_OR_RETRY`` and optionally ``VISIBLE_CONTENT_MAY_BE_INCOMPLETE``
    """
    if not is_partial:
        return

    limitations = score_bundle.get("limitations") or []
    codes = _lim_codes(limitations)
    if not codes:
        return

    issues: list[Issue] = list(score_bundle.get("issues") or [])
    recs: list[Recommendation] = list(score_bundle.get("recommendations") or [])

    has_strong = bool(codes & _STRONG_LIMITATION_CODES)
    is_spa = (pipeline_context or {}).get("is_probably_spa") is True
    has_thin = "THIN_PAGE" in codes
    has_thin_js = has_thin and is_spa

    sparse_outputs = len(issues) < 2 and len(recs) < 2
    # Strong fetch/render limits, or thin visible text on a likely SPA shell
    fill_sparse_report = sparse_outputs and (has_strong or has_thin_js)

    if fill_sparse_report and not _already_has_code(issues, _ISSUE_CODE):
        desc_parts: list[str] = []
        if "PLAYWRIGHT_FAILED" in codes:
            desc_parts.append(
                "Headless rendering did not complete successfully, so the HTML used for analysis may be incomplete."
            )
        if "PLAYWRIGHT_NO_GAIN" in codes:
            desc_parts.append(
                "A headless render ran but did not improve visible text enough; the HTTP snapshot may still be thin."
            )
        if "FETCH_DEGRADED" in codes:
            desc_parts.append("The HTTP response was incomplete, blocked, or not fully usable for analysis.")
        if "PARTIAL_PIPELINE" in codes:
            desc_parts.append("The pipeline marked this run as partial (thin capture, limits, or bot defenses).")
        if has_thin_js and "THIN_PAGE" in codes:
            desc_parts.append(
                "Very little visible text was extracted — common when the real content loads in the browser via JavaScript."
            )
        if not desc_parts:
            desc_parts.append("Analysis ran under degraded capture conditions.")

        issues.append(
            Issue(
                code=_ISSUE_CODE,
                title="Page capture was limited — scores and issues may not reflect the full page",
                description=" ".join(desc_parts),
                severity="medium",
                impact_scope="system",
                evidence={"limitation_codes": sorted(codes)},
                fix_priority=1,
            )
        )

        retry_bits: list[str] = [
            "Re-run the scan after ensuring headless Chromium is installed and Playwright is enabled on the server, if you rely on JS rendering.",
            "If the site blocks bots, try again from an environment that can render the page fully, or compare with what you see in a normal browser.",
            "Treat SEO/GEO scores as directional until capture quality improves.",
        ]
        if "PLAYWRIGHT_FAILED" in codes:
            retry_bits.insert(
                0,
                "Fix Playwright/browser installation on the analyzer host, then rescan — analysis may stay incomplete until rendering works.",
            )

        recs.append(
            Recommendation(
                key=_RECO_RETRY,
                title="Improve capture quality, then rescan",
                explanation=" ".join(retry_bits[:4]),
                impact_scope="system",
                priority=1,
                effort="medium",
                expected_gain="More reliable scores and issue list",
            )
        )

    # Secondary: JS-heavy undercapture but deterministic rules still produced several issues (no sparse bundle above)
    elif (
        has_thin_js
        and not sparse_outputs
        and len(recs) < 2
        and not _already_has_reco_key(recs, _RECO_VISIBLE)
        and not _already_has_reco_key(recs, _RECO_RETRY)
    ):
        recs.append(
            Recommendation(
                key=_RECO_VISIBLE,
                title="Visible text may be under-captured on this page",
                explanation=(
                    "The page looks JS-heavy and the captured text is very short. "
                    "Scores and rules may reflect only the initial HTML shell. "
                    "Retry with full rendering enabled, or verify the page in a browser."
                ),
                impact_scope="system",
                priority=2,
                effort="low",
                expected_gain="Clearer picture of real on-page content",
            )
        )

    score_bundle["issues"] = issues
    score_bundle["recommendations"] = recs
