"""Normalized extraction from DOM — placeholder until Sprint 2."""

from app.schemas.extraction import ExtractionSchema


class ExtractionService:
    def build_placeholder(self, scan_id: str) -> ExtractionSchema:
        return ExtractionSchema(scan_id=scan_id)


extraction_service = ExtractionService()
