#!/usr/bin/env python3
"""
Optional local E2E check against a running API (no pytest required).

  cd backend && uvicorn app.main:app --reload
  python scripts/verify_scan_api.py --base http://127.0.0.1:8000 --email dev@example.com --url https://example.com

Steps: POST /api/auth/session → Bearer → POST scan → poll GET → PATCH page-type → POST rescan → public report → GET public (no Bearer).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from typing import Any


def _req(
    method: str,
    url: str,
    data: dict[str, Any] | None = None,
    *,
    timeout: float = 30.0,
    bearer: str | None = None,
) -> tuple[int, Any]:
    body = None
    headers = {"Accept": "application/json"}
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
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
            payload = json.loads(err)
        except json.JSONDecodeError:
            payload = err
        return e.code, payload


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://127.0.0.1:8000", help="API root without trailing slash")
    p.add_argument("--email", default="dev@example.com", help="Email for POST /api/auth/session")
    p.add_argument("--url", default="https://example.com", help="URL to scan")
    p.add_argument("--poll-interval", type=float, default=1.0)
    p.add_argument("--timeout", type=float, default=120.0)
    args = p.parse_args()
    base = args.base.rstrip("/")

    code, health = _req("GET", f"{base}/health")
    if code != 200:
        print("health check failed:", code, health, file=sys.stderr)
        return 1
    print("health:", health)

    code, session = _req("POST", f"{base}/api/auth/session", {"email": args.email})
    if code not in (200, 201) or not isinstance(session, dict):
        print("POST /api/auth/session failed:", code, session, file=sys.stderr)
        return 1
    token = session.get("access_token")
    if not token or not isinstance(token, str):
        print("no access_token in session response:", session, file=sys.stderr)
        return 1
    print("session ok for", session.get("user", {}).get("email", args.email))

    code, created = _req("POST", f"{base}/api/scans", {"url": args.url}, bearer=token)
    if code not in (200, 201):
        print("POST /api/scans failed:", code, created, file=sys.stderr)
        return 1
    scan_id = str(created["scan_id"])
    print("created scan", scan_id, "status", created.get("status"))

    terminal = frozenset({"completed", "partial", "failed"})
    deadline = time.monotonic() + args.timeout
    last_status = ""
    while time.monotonic() < deadline:
        code, detail = _req("GET", f"{base}/api/scans/{scan_id}", bearer=token)
        if code != 200:
            print("GET scan failed:", code, detail, file=sys.stderr)
            return 1
        last_status = str(detail.get("status", ""))
        print("poll:", last_status, "scores", detail.get("global_score"))
        if last_status in terminal:
            break
        time.sleep(args.poll_interval)
    else:
        print("timeout waiting for terminal status, last=", last_status, file=sys.stderr)
        return 1

    code, patched = _req(
        "PATCH",
        f"{base}/api/scans/{scan_id}/page-type",
        {"page_type": "article"},
        bearer=token,
    )
    print("PATCH page-type:", code, patched.get("status") if isinstance(patched, dict) else patched)

    code, rescan = _req("POST", f"{base}/api/scans/{scan_id}/rescan", None, bearer=token)
    if code not in (200, 201):
        print("rescan failed:", code, rescan, file=sys.stderr)
        return 1
    child = str(rescan["scan_id"])
    print("rescan child", child)

    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        code, d2 = _req("GET", f"{base}/api/scans/{child}", bearer=token)
        if code != 200:
            print("GET child failed:", code, d2, file=sys.stderr)
            return 1
        st = str(d2.get("status", ""))
        print("child poll:", st)
        if st in terminal:
            break
        time.sleep(args.poll_interval)

    code, pub = _req("POST", f"{base}/api/scans/{scan_id}/public-report", None, bearer=token)
    if code not in (200, 201):
        print("public-report failed:", code, pub, file=sys.stderr)
        return 1
    pid = pub["public_id"]
    code, pr = _req("GET", f"{base}/api/public-reports/{pid}")
    print("public GET (no auth):", code, "global", pr.get("global_score") if isinstance(pr, dict) else pr)

    print("OK — flow finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
