"""Page type heuristics — placeholder until Sprint 3 (pipeline-analysis.md)."""

from typing import Any


class PageTypeService:
    def detect_placeholder(self, normalized_url: str, path: str) -> dict[str, Any]:
        return {
            "page_type_detected": "other",
            "page_type_confidence": 0.0,
            "candidates": {},
        }


page_type_service = PageTypeService()
