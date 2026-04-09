"""Playwright-based rendering — placeholder until Sprint 2 (see docs/01-architecture/pipeline-analysis.md)."""

from typing import Any


class RenderService:
    async def fetch_or_render(self, scan_id: str, normalized_url: str) -> dict[str, Any]:
        """Escalate from lightweight fetch to Playwright when needed; not implemented in scaffold."""
        return {
            "fetch_method": "placeholder",
            "render_success": False,
            "final_url": None,
            "http_status": None,
            "note": "Implement Playwright render in Sprint 2",
        }


render_service = RenderService()
