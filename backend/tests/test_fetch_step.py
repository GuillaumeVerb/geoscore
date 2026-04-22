"""HTTP fetch: retries and headers (no real network)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx

from app.services.pipeline.fetch_step import BROWSER_LIKE_USER_AGENT, http_fetch


def test_http_fetch_success_first_try() -> None:
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html>ok</html>"
    mock_resp.url = "https://example.com/"
    mock_resp.headers = {"content-type": "text/html; charset=utf-8"}

    with patch("app.services.pipeline.fetch_step.httpx.Client") as client_cls:
        inst = MagicMock()
        client_cls.return_value.__enter__.return_value = inst
        inst.get.return_value = mock_resp
        out = http_fetch("https://example.com/", max_retries=0)
        assert out.ok is True
        assert "<html>ok" in out.html
        assert out.load_time_ms >= 0
        inst.get.assert_called_once()


def test_http_fetch_retries_on_503() -> None:
    bad = MagicMock()
    bad.status_code = 503
    bad.text = "unavailable"
    bad.url = "https://example.com/"
    bad.headers = {"content-type": "text/html"}
    good = MagicMock()
    good.status_code = 200
    good.text = "<html>ok</html>"
    good.url = "https://example.com/"
    good.headers = {"content-type": "text/html"}

    with patch("app.services.pipeline.fetch_step.httpx.Client") as client_cls:
        inst = MagicMock()
        client_cls.return_value.__enter__.return_value = inst
        inst.get.side_effect = [bad, good]
        out = http_fetch("https://example.com/", max_retries=1)
        assert out.ok is True
        assert inst.get.call_count == 2


def test_httpx_uses_browser_like_user_agent() -> None:
    assert "Chrome" in BROWSER_LIKE_USER_AGENT
    assert "Gecko" in BROWSER_LIKE_USER_AGENT


def test_http_fetch_request_error_retry() -> None:
    with patch("app.services.pipeline.fetch_step.httpx.Client") as client_cls:
        inst = MagicMock()
        client_cls.return_value.__enter__.return_value = inst
        inst.get.side_effect = [
            httpx.RequestError("Connection refused", request=MagicMock()),
            _ok_response(),
        ]
        out = http_fetch("https://example.com/retry", max_retries=1)
        assert out.ok is True
        assert inst.get.call_count == 2


def _ok_response() -> MagicMock:
    good = MagicMock()
    good.status_code = 200
    good.text = "<html>ok</html>"
    good.url = "https://example.com/retry"
    good.headers = {"content-type": "text/html"}
    return good
