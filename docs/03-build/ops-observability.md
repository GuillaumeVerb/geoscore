# Operations: observability, rate limits, and per-host fetch tuning

## Scan pipeline logs

Successful and failed scan runs emit a single grep-friendly line from the API process:

```text
scan_pipeline_outcome scan_id=… host=… final_status=… [error_code=…] [partial=…] fetch_method=… load_time_ms=…
```

- **host**: hostname of the normalized URL.
- **final_status**: `completed`, `partial`, or `failed`.
- **error_code**: e.g. `HTTP_ERROR`, `INSUFFICIENT_CAPTURE`, `FETCH_ERROR` when `failed`.
- **partial**: `True` / `False` when the run completed with scores.
- **fetch_method**: HTTP-only vs Playwright paths (see pipeline constants).
- **load_time_ms**: combined HTTP (+ Playwright if used) timing where applicable.

Ship these logs to your platform’s log search (Railway, CloudWatch, etc.) to see which hosts fail often before changing product rules.

## Rate limiting new scans and rescans

`POST /api/scans` and `POST /api/scans/{scan_id}/rescan` share one limit per **authenticated user** (in-process rolling window). Each new scan and each rescan count toward the same quota.

| Env / setting | Default | Meaning |
|---------------|---------|--------|
| `SCAN_CREATE_PER_MINUTE` | `30` | Max (new scans + rescans) per user per ~60s |

Set to `0` to disable the limit (not recommended in production). For **multiple API replicas**, replace this with a shared store (e.g. Redis) — the current implementation is per process.

## Per-host fetch tuning

See `backend/.env.example` and `host_config.py` for:

- `HTTP_TIMEOUT_BOOST_HOSTS` — extra seconds on slow HTTP responses.
- `PLAYWRIGHT_TIMEOUT_BOOST_HOSTS` / `PLAYWRIGHT_HOST_TIMEOUT_BOOST_MS` — extra time for headless render.
- `PLAYWRIGHT_RESOURCE_BLOCK_EXEMPT_HOSTS` — do not block heavy assets (rare; when text appears very late).

Host lists accept comma-separated hostnames and `*.example.com` rules.

## Related

- [database-migrations.md](database-migrations.md) for schema changes.
- Product constraints in repo root `AGENTS.md` (scoring version frozen; bounded LLM).
