"""Provider-agnostic LLM layer — interface only; optional and bounded per docs/02-scoring/llm-strategy.md."""

from __future__ import annotations

from typing import Any, Protocol


class LLMServiceProtocol(Protocol):
    def analyze_bounded(self, scan_id: str, payload: dict[str, Any]) -> dict[str, Any] | None: ...


class LLMService:
    """No provider calls in scaffold; failures must not break deterministic path."""

    def analyze_bounded(self, scan_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        return None


llm_service = LLMService()
