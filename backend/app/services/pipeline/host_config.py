"""
Parse hostname lists for per-origin fetch / Playwright overrides (comma-separated env).
Supports exact host or ``*.example.com`` suffix rules.
"""

from __future__ import annotations

from urllib.parse import urlparse


def _normalize_hostname(hostname: str | None) -> str | None:
    if not hostname:
        return None
    h = hostname.lower().strip()
    if h.startswith("www."):
        return h[4:]
    return h


def host_matches_rule(host: str, rule: str) -> bool:
    """
    `rule` is one entry: `example.com` (exact) or `*.example.com` (this host or any subdomain).
    """
    rule = (rule or "").strip().lower()
    if not rule:
        return False
    if rule.startswith("www."):
        rule = rule[4:]
    if rule.startswith("*."):
        root = rule[2:]
        return host == root or host.endswith("." + root)
    return host == rule


def url_host_in_csv(url: str, hosts_csv: str) -> bool:
    """True when URL's hostname matches any non-empty entry in the comma-separated list."""
    if not (hosts_csv or "").strip():
        return False
    try:
        host = _normalize_hostname(urlparse(url).hostname)
    except (ValueError, TypeError, AttributeError):
        return False
    if not host:
        return False
    for part in hosts_csv.split(","):
        p = (part or "").strip()
        if p and host_matches_rule(host, p):
            return True
    return False
