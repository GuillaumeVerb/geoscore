#!/usr/bin/env python3
"""
Calibration batch: run GeoScore-style analysis on a URL corpus and export JSON + Markdown.

Modes:
  --mode api     POST /api/scans + poll GET (needs uvicorn + Postgres; full pipeline incl. optional Playwright)
  --mode offline HTTP fetch + extract + deterministic score only (no DB; no Playwright)

Each row includes validation_context (page types, fetch_method, partial, is_probably_spa, pipeline_context,
word_count, heading/link counts, FAQ/example/number booleans, limitations_top) for quick human review.

Examples:
  cd backend && python scripts/run_calibration.py --mode offline --out-dir calibration/out
  cd backend && python scripts/run_calibration.py --mode api --base http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

# Offline stack (repo root = backend parent for imports)
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


def _load_corpus(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("corpus must be a JSON array")
    return data


def _enum_str(value: Any) -> Any:
    if value is None:
        return None
    return getattr(value, "value", value)


def _extraction_as_dict(extraction: Any) -> dict[str, Any]:
    if extraction is None:
        return {}
    if isinstance(extraction, dict):
        return extraction
    if hasattr(extraction, "model_dump"):
        return extraction.model_dump(mode="json")
    return {}


def _build_validation_context(
    extraction_raw: Any,
    *,
    page_type_detected: Any,
    page_type_final: Any,
    status: Any,
    partial: bool | None,
    fetch_method: str | None,
    is_probably_spa: bool | None,
    limitations: list[Any],
) -> dict[str, Any]:
    """Compact snapshot for calibration exports (no DB round-trip)."""
    extraction = _extraction_as_dict(extraction_raw)
    content = extraction.get("content") or {}
    struct = content.get("structural_features") or {}
    headings = extraction.get("headings") or {}
    answ = content.get("answerability_features") or {}
    prec = content.get("precision_features") or {}
    links = extraction.get("links") or {}
    fetch_info = extraction.get("fetch_info") or {}

    h1c = int(headings.get("h1_count") or 0)
    h2c = int(struct.get("h2_count") or headings.get("h2_count") or 0)

    has_faq = bool(struct.get("has_faq_section_heuristic")) or bool(answ.get("faq_schema_present"))
    ex_hits = int(prec.get("example_phrase_hits") or 0)
    has_examples = ex_hits > 0
    years = int(prec.get("year_mentions") or 0)
    has_currency = bool(prec.get("currency_or_price_mentions"))
    has_numbers = years > 0 or has_currency

    lim_top: list[dict[str, Any]] = []
    for lim in (limitations or [])[:8]:
        if isinstance(lim, dict):
            lim_top.append(
                {
                    "code": lim.get("code"),
                    "severity": lim.get("severity"),
                    "message": (str(lim.get("message") or ""))[:240],
                }
            )

    pc = extraction.get("pipeline_context")
    pc_out: dict[str, Any] = dict(pc) if isinstance(pc, dict) else {}

    fetch_resolved = fetch_method or fetch_info.get("primary_fetch_method") or pc_out.get("primary_fetch_method")
    partial_resolved = partial if partial is not None else pc_out.get("partial")
    spa_resolved = is_probably_spa if is_probably_spa is not None else pc_out.get("is_probably_spa")

    return {
        "page_type_detected": _enum_str(page_type_detected),
        "page_type_final": _enum_str(page_type_final),
        "status": _enum_str(status),
        "fetch_method": fetch_resolved,
        "is_probably_spa": spa_resolved,
        "partial": partial_resolved,
        "pipeline_context": pc_out if pc_out else None,
        "extraction_present": bool(extraction),
        "word_count": int(content.get("word_count") or 0),
        "h1_count": h1c,
        "h2_count": h2c,
        "internal_links_count": int(links.get("internal_count") or 0),
        "has_faq": has_faq,
        "has_examples": has_examples,
        "has_numbers": has_numbers,
        "limitations_top": lim_top,
    }


def _req_api(method: str, url: str, data: dict[str, Any] | None = None, timeout: float = 60.0) -> tuple[int, Any]:
    body = None
    headers = {"Accept": "application/json"}
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(err)
        except json.JSONDecodeError:
            return e.code, err
    except urllib.error.URLError as e:
        # Connection refused, DNS, timeout, etc. — avoid traceback; callers use code -1
        reason = getattr(e.reason, "strerror", None) or str(e.reason)
        return -1, {"error": reason, "url_error": str(e)}


def _run_offline(url: str) -> dict[str, Any]:
    from app.core.url_norm import normalize_submitted_url
    from app.services.pipeline.constants import FETCH_METHOD_HTTP
    from app.services.pipeline.extract_step import build_extraction_payload
    from app.services.pipeline.fetch_step import http_fetch
    from app.services.pipeline.page_type_step import detect_page_type
    from app.services.pipeline.render_fallback_decision import analyze_http_html_signals, is_probably_spa
    from app.services.pipeline.score_minimal import run_deterministic_score

    norm, _, path = normalize_submitted_url(url)
    out = http_fetch(norm, timeout_sec=28.0)
    html = out.html or ""
    fetch_info = {
        "mode": "offline_http_only",
        "http_status": out.http_status,
        "final_url": out.final_url,
        "load_time_ms": out.load_time_ms,
        "primary_fetch_method": FETCH_METHOD_HTTP,
    }
    render_info = {"engine": "offline_no_playwright", "note": "Calibration offline — no Playwright fallback"}
    sid = uuid4()
    extraction = build_extraction_payload(sid, norm, fetch_info, render_info, html)
    meta = extraction.get("meta") or {}
    title = (meta.get("title") or "").strip()
    h1s = (extraction.get("headings") or {}).get("h1") or []
    h1_list = h1s if isinstance(h1s, list) else []
    page_type, _conf = detect_page_type(path or "/", title, h1_list)
    fetch_ok = bool(out.ok and (out.http_status is None or out.http_status < 400))
    partial = not fetch_ok or (out.http_status is not None and out.http_status >= 400) or len(html) < 500
    sig = analyze_http_html_signals(html, path or "/")
    spa = is_probably_spa(sig)
    extraction["pipeline_context"] = {
        "partial": partial,
        "is_probably_spa": spa,
        "primary_fetch_method": FETCH_METHOD_HTTP,
    }
    score = run_deterministic_score(
        extraction,
        page_type=page_type,
        fetch_ok=fetch_ok,
        http_status=out.http_status,
        partial=partial,
    )
    issues_out = [i.model_dump() for i in score["issues"]]
    recs_out = [r.model_dump() for r in score["recommendations"]]
    lims_dump = [L.model_dump() for L in score["limitations"]]
    st = "completed" if not partial else "partial"
    validation = _build_validation_context(
        extraction,
        page_type_detected=page_type,
        page_type_final=None,
        status=st,
        partial=partial,
        fetch_method=FETCH_METHOD_HTTP,
        is_probably_spa=spa,
        limitations=lims_dump,
    )
    return {
        "source": "offline",
        "url": url,
        "normalized_url": norm,
        "http_status": out.http_status,
        "page_type_detected": page_type,
        "page_type_final": None,
        "status": st,
        "global_score": score["global_score"],
        "seo_score": score["seo_score"],
        "geo_score": score["geo_score"],
        "analysis_confidence": score["analysis_confidence"],
        "confidence_score": score["confidence_score"],
        "summary": score["summary"],
        "issues": issues_out,
        "recommendations": recs_out,
        "limitations": lims_dump,
        "strengths": score["strengths"],
        "issue_codes": [i["code"] for i in issues_out],
        "rec_keys": [r.get("key") for r in recs_out],
        "word_count": (extraction.get("content") or {}).get("word_count"),
        "validation_context": validation,
    }


def _run_api(base: str, url: str, poll_interval: float, timeout: float) -> dict[str, Any]:
    base = base.rstrip("/")
    code, created = _req_api("POST", f"{base}/api/scans", {"url": url})
    if code == -1:
        return {"source": "api", "url": url, "error": "api_unreachable", "detail": created}
    if code not in (200, 201) or not isinstance(created, dict):
        return {"source": "api", "url": url, "error": f"POST scans failed {code}", "detail": created}
    scan_id = created["scan_id"]
    deadline = time.monotonic() + timeout
    detail: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        c2, d2 = _req_api("GET", f"{base}/api/scans/{scan_id}")
        if c2 != 200 or not isinstance(d2, dict):
            return {"source": "api", "url": url, "error": f"GET scan failed {c2}", "detail": d2}
        detail = d2
        st = str(d2.get("status", ""))
        if st in ("completed", "partial", "failed"):
            break
        time.sleep(poll_interval)
    else:
        return {"source": "api", "url": url, "scan_id": scan_id, "error": "poll_timeout", "last": detail}

    assert detail is not None
    issues = detail.get("issues") or []
    recs = detail.get("recommendations") or []
    lims = detail.get("limitations") or []
    st = detail.get("status")
    extraction = detail.get("extraction")
    exd = _extraction_as_dict(extraction)
    pc = exd.get("pipeline_context") if isinstance(exd.get("pipeline_context"), dict) else {}
    st_str = _enum_str(st)
    if isinstance(pc.get("partial"), bool):
        partial_flag = bool(pc["partial"])
    elif st_str == "partial":
        partial_flag = True
    elif st_str == "completed":
        partial_flag = False
    else:
        partial_flag = None
    spa_flag = pc.get("is_probably_spa") if isinstance(pc.get("is_probably_spa"), bool) else None
    fetch_m = (exd.get("fetch_info") or {}).get("primary_fetch_method") or pc.get("primary_fetch_method")

    validation = _build_validation_context(
        extraction,
        page_type_detected=detail.get("page_type_detected"),
        page_type_final=detail.get("page_type_final"),
        status=st,
        partial=partial_flag,
        fetch_method=fetch_m if isinstance(fetch_m, str) else None,
        is_probably_spa=spa_flag,
        limitations=lims,
    )

    return {
        "source": "api",
        "url": url,
        "scan_id": str(detail.get("scan_id")),
        "status": detail.get("status"),
        "page_type_detected": detail.get("page_type_detected"),
        "page_type_final": detail.get("page_type_final"),
        "global_score": detail.get("global_score"),
        "seo_score": detail.get("seo_score"),
        "geo_score": detail.get("geo_score"),
        "analysis_confidence": detail.get("analysis_confidence"),
        "confidence_score": (detail.get("scores") or {}).get("confidence_score") if isinstance(detail.get("scores"), dict) else None,
        "summary": detail.get("summary"),
        "issues": issues,
        "recommendations": recs,
        "limitations": lims,
        "strengths": detail.get("strengths") or [],
        "issue_codes": [i.get("code") for i in issues if isinstance(i, dict)],
        "rec_keys": [r.get("key") for r in recs if isinstance(r, dict)],
        "error_code": detail.get("error_code"),
        "error_message": detail.get("error_message"),
        "validation_context": validation,
    }


def _heuristics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Lightweight flags for calibration review (not model quality)."""
    flags: list[dict[str, Any]] = []
    code_counts: Counter[str] = Counter()
    key_counts: Counter[str] = Counter()
    for row in rows:
        if row.get("error"):
            continue
        codes = [c for c in row.get("issue_codes") or [] if c]
        code_counts.update(codes)
        keys = [k for k in row.get("rec_keys") or [] if k]
        key_counts.update(keys)
        n_issues = len(row.get("issues") or [])
        if n_issues >= 9:
            flags.append({"id": row.get("id"), "url": row.get("url"), "flag": "many_issues", "count": n_issues})
        g = row.get("global_score")
        if isinstance(g, (int, float)) and g is not None and g < 38:
            flags.append({"id": row.get("id"), "url": row.get("url"), "flag": "very_low_global", "global_score": g})
        if isinstance(g, (int, float)) and g is not None and g > 92 and row.get("status") == "partial":
            flags.append({"id": row.get("id"), "flag": "high_score_partial", "global_score": g})

    return {
        "issue_code_frequency": dict(code_counts.most_common(25)),
        "recommendation_key_frequency": dict(key_counts.most_common(15)),
        "row_flags": flags,
    }


def _markdown_report(meta: dict[str, Any], rows: list[dict[str, Any]], heur: dict[str, Any]) -> str:
    lines = [
        "# GeoScore calibration run",
        "",
        f"- Generated: {meta.get('generated_at')}",
        f"- Mode: **{meta.get('mode')}**",
        f"- Corpus: {meta.get('corpus_path')}",
        "",
        "## Summary table",
        "",
        "| id | category | status | global | SEO | GEO | confidence | issues | top issue |",
        "|----|----------|--------|--------|-----|-----|------------|--------|-----------|",
    ]
    for r in rows:
        issues = r.get("issues") or []
        top = ""
        if issues and isinstance(issues[0], dict):
            top = (issues[0].get("code") or issues[0].get("title") or "")[:40]
        lines.append(
            f"| {r.get('id','')} | {r.get('category','')} | {r.get('status','?')} | "
            f"{r.get('global_score','')} | {r.get('seo_score','')} | {r.get('geo_score','')} | "
            f"{r.get('analysis_confidence','')} | {len(issues)} | {top} |"
        )
    lines.extend(
        [
            "",
            "## Frequent issue codes",
            "",
            "```",
            json.dumps(heur.get("issue_code_frequency"), indent=2),
            "```",
            "",
            "## Frequent recommendation keys",
            "",
            "```",
            json.dumps(heur.get("recommendation_key_frequency"), indent=2),
            "```",
            "",
            "## Heuristic flags",
            "",
            "```",
            json.dumps(heur.get("row_flags"), indent=2),
            "```",
            "",
            "## Per-page detail (top issues & recs)",
            "",
        ]
    )
    for r in rows:
        lines.append(f"### `{r.get('id')}` — {r.get('url')}")
        lines.append(f"- **Category:** {r.get('category')}")
        if r.get("error"):
            lines.append(f"- **Error:** {r.get('error')}")
            lines.append("")
            continue
        lines.append(f"- **Scores:** global {r.get('global_score')} · SEO {r.get('seo_score')} · GEO {r.get('geo_score')}")
        lines.append(f"- **Confidence:** {r.get('analysis_confidence')} ({r.get('confidence_score')})")
        lines.append(f"- **Summary:** {r.get('summary') or '—'}")
        vc = r.get("validation_context")
        if isinstance(vc, dict) and vc:
            lines.append(
                f"- **Context:** type `{vc.get('page_type_detected')}` → final `{vc.get('page_type_final')}` · "
                f"status `{vc.get('status')}` · fetch `{vc.get('fetch_method')}` · "
                f"partial={vc.get('partial')} · spa={vc.get('is_probably_spa')}"
            )
            lines.append(
                f"- **Extract signals:** words={vc.get('word_count')} · "
                f"H1={vc.get('h1_count')} H2={vc.get('h2_count')} · "
                f"internal_links={vc.get('internal_links_count')} · "
                f"faq={vc.get('has_faq')} · examples={vc.get('has_examples')} · numbers={vc.get('has_numbers')}"
            )
            pc = vc.get("pipeline_context")
            if pc:
                lines.append(f"- **pipeline_context:** `{json.dumps(pc, ensure_ascii=False)}`")
        lims = r.get("limitations") or []
        if lims:
            lines.append("- **Limitations (report):**")
            for L in lims[:8]:
                if isinstance(L, dict):
                    lines.append(f"  - `{L.get('code')}`: {L.get('message', '')[:120]}")
        lines.append("- **Top issues:**")
        for i in (r.get("issues") or [])[:5]:
            if isinstance(i, dict):
                lines.append(f"  - `{i.get('code')}` — {i.get('title')}")
        lines.append("- **Top recommendations:**")
        for rec in (r.get("recommendations") or [])[:5]:
            if isinstance(rec, dict):
                lines.append(f"  - `{rec.get('key')}` — {rec.get('title')}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Run calibration batch on corpus URLs")
    p.add_argument("--corpus", type=Path, default=_BACKEND_ROOT / "calibration" / "corpus.json")
    p.add_argument("--mode", choices=("api", "offline"), default="offline")
    p.add_argument("--base", default="http://127.0.0.1:8000", help="API root (api mode)")
    p.add_argument("--out-dir", type=Path, default=_BACKEND_ROOT / "calibration" / "out")
    p.add_argument("--poll-interval", type=float, default=1.5)
    p.add_argument("--timeout", type=float, default=180.0)
    args = p.parse_args()

    corpus = _load_corpus(args.corpus)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows: list[dict[str, Any]] = []

    if args.mode == "api":
        code, health = _req_api("GET", f"{args.base.rstrip('/')}/health", timeout=10.0)
        if code != 200:
            detail = ""
            if isinstance(health, dict) and health.get("error"):
                detail = f" — {health['error']}"
            status_txt = "unreachable (network)" if code == -1 else f"HTTP {code}"
            print(
                f"API health check failed at {args.base!r} ({status_txt}){detail}.\n"
                "  Start the backend (e.g. uvicorn on that host/port with Postgres) or run without the API:\n"
                "  PYTHONPATH=. python scripts/run_calibration.py --mode offline --out-dir calibration/out",
                file=sys.stderr,
            )
            return 1

    for entry in corpus:
        eid = entry.get("id", "")
        url = entry.get("url", "")
        cat = entry.get("category", "")
        print(f"… {eid} {url}", flush=True)
        if args.mode == "offline":
            try:
                payload = _run_offline(url)
            except Exception as ex:
                payload = {"source": "offline", "url": url, "error": str(ex)[:500]}
        else:
            payload = _run_api(args.base, url, args.poll_interval, args.timeout)
        payload["id"] = eid
        payload["category"] = cat
        rows.append(payload)

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "corpus_path": str(args.corpus),
        "n_urls": len(rows),
        "row_fields": {
            "validation_context": "page_type_detected, page_type_final, status, fetch_method, is_probably_spa, partial, pipeline_context, extraction_present, word_count, h1_count, h2_count, internal_links_count, has_faq, has_examples, has_numbers, limitations_top",
        },
    }
    heur = _heuristics(rows)
    out_json = args.out_dir / f"calibration_{stamp}.json"
    out_md = args.out_dir / f"calibration_{stamp}.md"
    out_json.write_text(
        json.dumps({"meta": meta, "heuristics": heur, "rows": rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    out_md.write_text(_markdown_report(meta, rows, heur), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
