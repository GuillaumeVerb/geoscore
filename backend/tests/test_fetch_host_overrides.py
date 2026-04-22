"""HTTP fetch: per-host extra timeout (mocked, no network)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.services.pipeline.fetch_step import http_fetch


@patch("app.services.pipeline.fetch_step._http_fetch_once")
def test_http_applies_extra_timeout_for_boost_host(mock_once: MagicMock) -> None:
    ok = MagicMock()
    ok.status_code = 200
    ok.text = "<html>ok</html>"
    ok.url = "https://example.com/"
    ok.headers = {"content-type": "text/html"}
    mock_once.return_value = MagicMock(
        ok=True,
        http_status=200,
        final_url="https://example.com/",
        content_type="text/html",
        html="<html>ok</html>",
        load_time_ms=1,
    )

    with patch("app.core.config.settings") as s:
        s.http_timeout_boost_hosts = "example.com"
        s.http_host_extra_timeout_sec = 4.0
        http_fetch("https://example.com/p", timeout_sec=10.0, max_retries=0)
    mock_once.assert_called_once()
    call_timeout = mock_once.call_args[0][1]
    assert call_timeout == 14.0


@patch("app.services.pipeline.fetch_step._http_fetch_once")
def test_http_no_extra_when_host_not_listed(mock_once: MagicMock) -> None:
    mock_once.return_value = MagicMock(
        ok=True,
        http_status=200,
        final_url="https://other.com/",
        content_type="text/html",
        html="<html>ok</html>",
        load_time_ms=1,
    )
    with patch("app.core.config.settings") as s:
        s.http_timeout_boost_hosts = "example.com"
        s.http_host_extra_timeout_sec = 4.0
        http_fetch("https://other.com/", timeout_sec=10.0, max_retries=0)
    assert mock_once.call_args[0][1] == 10.0
