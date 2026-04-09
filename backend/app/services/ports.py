"""Service-layer ports (interfaces) for scan workflow and public reports."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.schemas.api_contracts import (
    PageTypeOverrideRequest,
    PublicReportCreatedResponse,
    PublicReportResponse,
    RescanResponse,
    ScanCreateRequest,
    ScanDetailResponse,
    ScanResponse,
)


class ScanWorkflowPort(Protocol):
    """Orchestrates scan lifecycle and public sharing (mock or Postgres implementation)."""

    def create_scan(self, body: ScanCreateRequest) -> ScanResponse:
        """Create a scan from a submitted URL."""
        ...

    def get_scan(self, scan_id: UUID) -> ScanDetailResponse:
        """Return status and result payload for a scan."""
        ...

    def rescan_scan(self, scan_id: UUID) -> RescanResponse:
        """Create a new scan row linked to an existing scan."""
        ...

    def override_page_type(self, scan_id: UUID, body: PageTypeOverrideRequest) -> ScanDetailResponse:
        """Set page_type_final and schedule rescoring (scoring not implemented in scaffold)."""
        ...

    def create_public_report(self, scan_id: UUID) -> PublicReportCreatedResponse:
        """Enable or create a shareable public id for this scan."""
        ...

    def get_public_report(self, public_id: str) -> PublicReportResponse:
        """Return reduced public view for a public_id."""
        ...
