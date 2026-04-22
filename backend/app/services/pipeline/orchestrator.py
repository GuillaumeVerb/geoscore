"""
Run scan pipeline: status transitions, persist fetch/extraction/scores/issues/recommendations.
HTTP fetch first; optional Playwright fallback when HTML looks like a JS shell (no LLM).
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.domain.enums import ScanStatus
from app.models.scan import Scan
from app.models.scan_extraction import ScanExtraction
from app.models.scan_fetch_result import ScanFetchResult
from app.models.scan_issue import ScanIssue
from app.models.scan_recommendation import ScanRecommendation
from app.models.scan_score import ScanScore
from app.services.pipeline.constants import (
    EXTRACTION_VERSION,
    FETCH_METHOD_HTTP,
    FETCH_METHOD_HTTP_PLAYWRIGHT_ATTEMPTED,
    FETCH_METHOD_HTTP_THEN_PLAYWRIGHT,
    RULESET_VERSION,
    SCORING_VERSION,
)
from app.services.pipeline.extract_step import build_extraction_payload
from app.services.pipeline.fetch_step import FetchOutcome, fetch_diagnostics_dict, http_fetch
from app.services.pipeline.page_type_step import detect_page_type
from app.services.pipeline.playwright_fetch import choose_html_after_playwright, playwright_fetch_html
from app.services.pipeline.render_fallback_decision import (
    is_probably_spa,
    should_trigger_playwright_fallback,
    visible_text_metrics,
)
from app.services.degraded_capture_fallback import enrich_score_bundle_for_degraded_capture
from app.services.pipeline.scan_pipeline_logging import log_scan_pipeline_outcome
from app.services.pipeline.score_minimal import run_deterministic_score

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _partial_from_fetch(out: FetchOutcome | None, html_len: int) -> bool:
    if out is None:
        return True
    if not out.ok:
        return True
    if out.http_status is not None and out.http_status >= 400:
        return True
    if html_len < 500:
        return True
    if out.is_blocked:
        return True
    return False


def schedule_scan_pipeline(scan_id: UUID) -> None:
    """Fire-and-forget background run (MVP: in-process thread)."""

    def _run() -> None:
        db = SessionLocal()
        try:
            run_scan_pipeline(db, scan_id)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("scan pipeline failed scan_id=%s", scan_id)
            try:
                db2 = SessionLocal()
                s = db2.get(Scan, scan_id)
                if s:
                    s.status = ScanStatus.FAILED.value
                    s.error_code = "PIPELINE_ERROR"
                    s.error_message = "Pipeline crashed"
                    s.completed_at = _utcnow()
                    db2.commit()
                db2.close()
            except Exception:
                logger.exception("failed to mark scan failed scan_id=%s", scan_id)
        finally:
            db.close()

    t = threading.Thread(target=_run, name=f"scan-{scan_id}", daemon=True)
    t.start()


def run_scan_pipeline(db: Session, scan_id: UUID) -> None:
    scan = db.get(Scan, scan_id)
    if scan is None:
        return

    scan.started_at = scan.started_at or _utcnow()
    scan.error_code = None
    scan.error_message = None

    # --- fetching ---
    scan.status = ScanStatus.FETCHING.value
    db.flush()

    out: FetchOutcome | None = None
    html = ""
    try:
        out = http_fetch(
            scan.normalized_url,
            timeout_sec=settings.http_timeout_sec,
            max_retries=settings.http_fetch_max_retries,
        )
        html = out.html or ""
    except Exception as e:
        logger.exception("fetch exception scan_id=%s", scan_id)
        scan.status = ScanStatus.FAILED.value
        scan.error_code = "FETCH_ERROR"
        scan.error_message = str(e)[:500]
        scan.completed_at = _utcnow()
        db.add(
            ScanFetchResult(
                scan_id=scan.id,
                fetch_method=FETCH_METHOD_HTTP,
                http_status=None,
                final_url=scan.normalized_url,
                content_type=None,
                html_size=0,
                load_time_ms=None,
                render_success=False,
                is_blocked=False,
                has_auth_wall=False,
            )
        )
        return

    scan.final_url = out.final_url or scan.normalized_url

    if not out.ok and out.http_status is not None and out.http_status >= 400:
        db.add(
            ScanFetchResult(
                scan_id=scan.id,
                fetch_method=FETCH_METHOD_HTTP,
                http_status=out.http_status,
                final_url=out.final_url,
                content_type=out.content_type,
                page_title=None,
                html_size=len(html),
                load_time_ms=out.load_time_ms,
                render_success=False,
                is_blocked=out.is_blocked,
                has_auth_wall=out.has_auth_wall,
                is_probably_spa=None,
                main_text_size=None,
            )
        )
        scan.status = ScanStatus.FAILED.value
        scan.error_code = "HTTP_ERROR"
        scan.error_message = f"HTTP {out.http_status}"
        scan.completed_at = _utcnow()
        log_scan_pipeline_outcome(
            scan.id,
            scan.normalized_url,
            final_status=ScanStatus.FAILED.value,
            error_code="HTTP_ERROR",
            fetch_method=FETCH_METHOD_HTTP,
            load_time_ms=out.load_time_ms,
        )
        return

    # --- rendering: optional Playwright if HTTP HTML looks like an empty SPA shell ---
    scan.status = ScanStatus.RENDERING.value
    db.flush()

    http_html = html
    trigger, signals = should_trigger_playwright_fallback(http_html, scan.path or "/", out)
    pw_result = None
    if trigger and settings.playwright_enabled:
        pw_result = playwright_fetch_html(
            out.final_url or scan.normalized_url,
            timeout_ms=settings.playwright_timeout_ms,
            settle_ms=settings.playwright_settle_ms,
            wait_for_load_state=settings.playwright_wait_for_load_state,
            load_state_timeout_ms=settings.playwright_load_state_timeout_ms,
            block_heavy_resources=settings.playwright_block_heavy_resources,
            retry=settings.playwright_retry,
        )

    final_html, choice, pw_diag = choose_html_after_playwright(http_html, pw_result)

    vw, vc = visible_text_metrics(final_html)
    if vw < 15 and len(final_html.strip()) < 300:
        db.add(
            ScanFetchResult(
                scan_id=scan.id,
                fetch_method=FETCH_METHOD_HTTP_PLAYWRIGHT_ATTEMPTED
                if (trigger and settings.playwright_enabled and pw_result is not None)
                else FETCH_METHOD_HTTP,
                http_status=out.http_status,
                final_url=out.final_url,
                content_type=out.content_type,
                page_title=None,
                html_size=len(final_html),
                main_text_size=vc,
                load_time_ms=out.load_time_ms + (pw_result.load_time_ms if pw_result else 0),
                render_success=False,
                is_blocked=out.is_blocked,
                has_auth_wall=out.has_auth_wall,
                is_probably_spa=is_probably_spa(signals),
            )
        )
        scan.status = ScanStatus.FAILED.value
        scan.error_code = "INSUFFICIENT_CAPTURE"
        scan.error_message = "Not enough rendered content after HTTP and optional Playwright"
        scan.completed_at = _utcnow()
        _insufficient_fm = (
            FETCH_METHOD_HTTP_PLAYWRIGHT_ATTEMPTED
            if (trigger and settings.playwright_enabled and pw_result is not None)
            else FETCH_METHOD_HTTP
        )
        _insufficient_load = out.load_time_ms + (pw_result.load_time_ms if pw_result else 0)
        log_scan_pipeline_outcome(
            scan.id,
            scan.normalized_url,
            final_status=ScanStatus.FAILED.value,
            error_code="INSUFFICIENT_CAPTURE",
            fetch_method=_insufficient_fm,
            load_time_ms=_insufficient_load,
        )
        return

    if choice == "playwright" and pw_result and pw_result.final_url:
        scan.final_url = pw_result.final_url
        final_url_for_row = pw_result.final_url
    else:
        final_url_for_row = out.final_url

    total_load_ms = out.load_time_ms + (pw_result.load_time_ms if pw_result else 0)
    if choice == "playwright":
        fetch_method_used = FETCH_METHOD_HTTP_THEN_PLAYWRIGHT
    elif trigger and settings.playwright_enabled and pw_result is not None:
        fetch_method_used = FETCH_METHOD_HTTP_PLAYWRIGHT_ATTEMPTED
    else:
        fetch_method_used = FETCH_METHOD_HTTP

    content_type_row = out.content_type if choice != "playwright" else "text/html"

    fetch_row = ScanFetchResult(
        scan_id=scan.id,
        fetch_method=fetch_method_used,
        http_status=out.http_status,
        final_url=final_url_for_row,
        content_type=content_type_row,
        page_title=None,
        html_size=len(final_html),
        main_text_size=vc,
        load_time_ms=total_load_ms,
        render_success=bool(final_html.strip()),
        is_blocked=out.is_blocked,
        has_auth_wall=out.has_auth_wall,
        is_probably_spa=is_probably_spa(signals),
    )
    db.add(fetch_row)
    db.flush()

    # --- extracting ---
    scan.status = ScanStatus.EXTRACTING.value
    db.flush()

    fetch_info: dict[str, Any] = {
        "primary_fetch_method": fetch_method_used,
        "http_status": out.http_status,
        "http_final_url": out.final_url,
        "http_load_time_ms": out.load_time_ms,
        "http_diagnostics": fetch_diagnostics_dict(out),
        "playwright_diagnostics": pw_diag,
        "fallback_trigger_reasons": signals.reasons_would_fallback,
    }
    render_info = {
        "engine": "playwright_chromium" if choice == "playwright" else "http",
        "html_choice": choice,
        "playwright_enabled": settings.playwright_enabled,
        "fallback_triggered": trigger,
    }

    extraction_payload = build_extraction_payload(
        scan.id,
        scan.normalized_url,
        fetch_info,
        render_info,
        final_html,
    )

    partial_for_score = _partial_from_fetch(out, len(final_html))
    if trigger and choice != "playwright":
        partial_for_score = True
    spa_flag = fetch_row.is_probably_spa
    if spa_flag is None:
        spa_flag = is_probably_spa(signals)
    extraction_payload["pipeline_context"] = {
        "partial": partial_for_score,
        "is_probably_spa": bool(spa_flag),
        "primary_fetch_method": fetch_method_used,
    }

    extra_limits: list[dict[str, str]] = []
    if trigger and not settings.playwright_enabled:
        extra_limits.append(
            {
                "code": "PLAYWRIGHT_DISABLED",
                "message": "Page matched JS-heavy fallback criteria but Playwright is disabled (PLAYWRIGHT_ENABLED).",
                "severity": "info",
            }
        )
    if trigger and pw_result and pw_result.skipped_reason == "playwright_package_not_installed":
        extra_limits.append(
            {
                "code": "PLAYWRIGHT_NOT_INSTALLED",
                "message": "Playwright package or browsers missing; install with: pip install playwright && playwright install chromium",
                "severity": "warning",
            }
        )
    elif trigger and pw_diag.get("playwright_error"):
        extra_limits.append(
            {
                "code": "PLAYWRIGHT_FAILED",
                "message": f"Headless render failed: {pw_diag['playwright_error'][:240]}",
                "severity": "warning",
            }
        )
    if choice == "http_kept_playwright_weak":
        extra_limits.append(
            {
                "code": "PLAYWRIGHT_NO_GAIN",
                "message": "Playwright ran but visible text did not improve enough vs HTTP; HTTP snapshot used.",
                "severity": "info",
            }
        )
    for lim in extra_limits:
        extraction_payload.setdefault("limitations", []).append(lim)

    meta = extraction_payload.get("meta") or {}
    title = (meta.get("title") or "").strip()
    h1s = (extraction_payload.get("headings") or {}).get("h1") or []

    page_type_detected, page_type_confidence = detect_page_type(scan.path or "/", title, h1s if isinstance(h1s, list) else [])
    scan.page_type_detected = page_type_detected
    scan.page_type_confidence = page_type_confidence
    if scan.page_type_final is None:
        scan.page_type_final = page_type_detected

    page_type_for_score = scan.page_type_final or page_type_detected

    ext_row = ScanExtraction(
        scan_id=scan.id,
        extraction_version=EXTRACTION_VERSION,
        extraction_payload=extraction_payload,
    )
    db.add(ext_row)
    db.flush()

    fetch_row.page_title = title or None

    fetch_ok = bool(out.ok and (out.http_status is None or out.http_status < 400))

    # --- scoring_rules ---
    scan.status = ScanStatus.SCORING_RULES.value
    db.flush()

    score_bundle = run_deterministic_score(
        extraction_payload,
        page_type=page_type_for_score,
        fetch_ok=fetch_ok,
        http_status=out.http_status,
        partial=partial_for_score,
    )
    enrich_score_bundle_for_degraded_capture(
        score_bundle,
        is_partial=partial_for_score,
        pipeline_context=extraction_payload.get("pipeline_context")
        if isinstance(extraction_payload.get("pipeline_context"), dict)
        else None,
    )

    # --- aggregating ---
    scan.status = ScanStatus.AGGREGATING.value
    db.flush()

    _replace_score_artifacts(
        db,
        scan.id,
        score_bundle,
    )

    scan.extraction_version = EXTRACTION_VERSION
    scan.scoring_version = SCORING_VERSION
    scan.ruleset_version = RULESET_VERSION
    scan.analysis_confidence = score_bundle["analysis_confidence"]
    scan.summary = score_bundle["summary"]
    scan.strengths = score_bundle["strengths"]
    scan.limitations = [l.model_dump() for l in score_bundle["limitations"]]

    scan.status = ScanStatus.PARTIAL.value if partial_for_score else ScanStatus.COMPLETED.value
    scan.completed_at = _utcnow()
    db.flush()
    log_scan_pipeline_outcome(
        scan.id,
        scan.normalized_url,
        final_status=scan.status,
        partial=partial_for_score,
        fetch_method=fetch_method_used,
        load_time_ms=total_load_ms,
    )


def _replace_score_artifacts(
    db: Session,
    scan_id: UUID,
    score_bundle: dict[str, Any],
) -> None:
    db.execute(delete(ScanScore).where(ScanScore.scan_id == scan_id))
    db.execute(delete(ScanIssue).where(ScanIssue.scan_id == scan_id))
    db.execute(delete(ScanRecommendation).where(ScanRecommendation.scan_id == scan_id))
    db.flush()

    db.add(
        ScanScore(
            scan_id=scan_id,
            scoring_version=SCORING_VERSION,
            ruleset_version=RULESET_VERSION,
            global_score=float(score_bundle["global_score"]),
            seo_score=float(score_bundle["seo_score"]),
            geo_score=float(score_bundle["geo_score"]),
            seo_subscores=dict(score_bundle["seo_subscores"] or {}),
            geo_subscores=dict(score_bundle["geo_subscores"] or {}),
            penalties=dict(score_bundle["penalties"] or {}),
            bonuses=dict(score_bundle["bonuses"] or {}),
            confidence_score=float(score_bundle["confidence_score"])
            if score_bundle.get("confidence_score") is not None
            else None,
        )
    )
    for iss in score_bundle["issues"]:
        db.add(
            ScanIssue(
                scan_id=scan_id,
                code=iss.code,
                title=iss.title,
                description=iss.description,
                severity=iss.severity,
                impact_scope=iss.impact_scope,
                evidence=dict(iss.evidence or {}),
                fix_priority=iss.fix_priority,
            )
        )
    for rec in score_bundle["recommendations"]:
        db.add(
            ScanRecommendation(
                scan_id=scan_id,
                key=rec.key,
                title=rec.title,
                explanation=rec.explanation or "",
                impact_scope=rec.impact_scope,
                priority=rec.priority,
                effort=rec.effort,
                expected_gain=rec.expected_gain,
            )
        )


def rescore_scan_only(db: Session, scan_id: UUID) -> bool:
    """Recompute scores from latest persisted extraction (no refetch)."""
    scan = db.get(Scan, scan_id)
    if scan is None:
        return False

    ext = (
        db.execute(
            select(ScanExtraction)
            .where(ScanExtraction.scan_id == scan_id)
            .order_by(ScanExtraction.created_at.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )
    if not ext or not ext.extraction_payload:
        return False

    fr = (
        db.execute(
            select(ScanFetchResult)
            .where(ScanFetchResult.scan_id == scan_id)
            .order_by(ScanFetchResult.created_at.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )
    html_len = int(fr.html_size or 0) if fr else 0
    pseudo = FetchOutcome(
        ok=bool(
            fr
            and fr.http_status is not None
            and fr.http_status < 400
            and html_len > 0
            and not (fr.is_blocked or False)
        ),
        http_status=fr.http_status if fr else None,
        final_url=fr.final_url if fr else scan.normalized_url,
        content_type=fr.content_type if fr else None,
        html="",
        load_time_ms=int(fr.load_time_ms or 0) if fr and fr.load_time_ms is not None else 0,
        error_message=None,
        is_blocked=bool(fr.is_blocked) if fr and fr.is_blocked is not None else False,
        has_auth_wall=bool(fr.has_auth_wall) if fr and fr.has_auth_wall is not None else False,
    )
    partial = _partial_from_fetch(pseudo, html_len)

    prev_ctx = (ext.extraction_payload or {}).get("pipeline_context") or {}
    pipeline_context: dict[str, Any] = {
        "partial": partial,
        "is_probably_spa": prev_ctx.get("is_probably_spa"),
        "primary_fetch_method": str(prev_ctx.get("primary_fetch_method") or ""),
    }
    if fr:
        if fr.is_probably_spa is not None:
            pipeline_context["is_probably_spa"] = bool(fr.is_probably_spa)
        if fr.fetch_method:
            pipeline_context["primary_fetch_method"] = str(fr.fetch_method)
    if pipeline_context.get("is_probably_spa") is None:
        pipeline_context["is_probably_spa"] = False
    else:
        pipeline_context["is_probably_spa"] = bool(pipeline_context["is_probably_spa"])
    score_payload = {**ext.extraction_payload, "pipeline_context": pipeline_context}

    scan.status = ScanStatus.SCORING_RULES.value
    db.flush()

    meta = ext.extraction_payload.get("meta") or {}
    title = (meta.get("title") or "").strip()
    h1s = (ext.extraction_payload.get("headings") or {}).get("h1") or []
    h1_list = h1s if isinstance(h1s, list) else []

    if scan.page_type_final:
        page_type_for_score = scan.page_type_final
    elif scan.page_type_detected:
        page_type_for_score = scan.page_type_detected
    else:
        page_type_for_score, _ = detect_page_type(scan.path or "/", title, h1_list)

    fetch_ok = bool(
        fr
        and fr.http_status is not None
        and fr.http_status < 400
        and html_len > 0
        and not (fr.is_blocked or False)
    )

    score_bundle = run_deterministic_score(
        score_payload,
        page_type=page_type_for_score,
        fetch_ok=fetch_ok,
        http_status=fr.http_status if fr else None,
        partial=partial,
    )
    enrich_score_bundle_for_degraded_capture(
        score_bundle,
        is_partial=partial,
        pipeline_context=score_payload.get("pipeline_context")
        if isinstance(score_payload.get("pipeline_context"), dict)
        else None,
    )

    scan.status = ScanStatus.AGGREGATING.value
    db.flush()

    _replace_score_artifacts(db, scan_id, score_bundle)

    scan.scoring_version = SCORING_VERSION
    scan.ruleset_version = RULESET_VERSION
    scan.analysis_confidence = score_bundle["analysis_confidence"]
    scan.summary = score_bundle["summary"]
    scan.strengths = score_bundle["strengths"]
    scan.limitations = [l.model_dump() for l in score_bundle["limitations"]]

    scan.status = ScanStatus.PARTIAL.value if partial else ScanStatus.COMPLETED.value
    scan.completed_at = _utcnow()
    return True
