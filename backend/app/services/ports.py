"""Service-layer ports (interfaces) for scan workflow and public reports."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.schemas.api_contracts import (
    PageTypeOverrideRequest,
    PublicReportCreatedResponse,
    PublicReportResponse,
    RescanResponse,
    ScanCompareResponse,
    ScanCreateRequest,
    ScanDetailResponse,
    ScanResponse,
    ScansListResponse,
)
from app.schemas.project import ProjectCreateRequest, ProjectRead, ProjectsListResponse


class ScanWorkflowPort(Protocol):
    """Orchestrates scan lifecycle and public sharing (mock or Postgres implementation)."""

    def create_scan(self, body: ScanCreateRequest, *, user_id: UUID) -> ScanResponse:
        """Create a scan from a submitted URL."""
        ...

    def get_scan(self, scan_id: UUID, *, user_id: UUID) -> ScanDetailResponse:
        """Return status and result payload for a scan owned by user_id."""
        ...

    def list_recent_scans(
        self, limit: int = 40, *, user_id: UUID, project_id: UUID | None = None
    ) -> ScansListResponse:
        """Recent scans for this user (newest first)."""
        ...

    def list_projects(self, *, user_id: UUID) -> ProjectsListResponse:
        ...

    def create_project(self, body: ProjectCreateRequest, *, user_id: UUID) -> ProjectRead:
        ...

    def get_scan_compare(self, scan_id: UUID, *, user_id: UUID) -> ScanCompareResponse:
        """Compare child scan to its parent (rescan lineage)."""
        ...

    def rescan_scan(self, scan_id: UUID, *, user_id: UUID) -> RescanResponse:
        """Create a new scan row linked to an existing scan."""
        ...

    def override_page_type(self, scan_id: UUID, body: PageTypeOverrideRequest, *, user_id: UUID) -> ScanDetailResponse:
        """Set page_type_final and schedule rescoring (scoring not implemented in scaffold)."""
        ...

    def create_public_report(self, scan_id: UUID, *, user_id: UUID) -> PublicReportCreatedResponse:
        """Enable or create a shareable public id for this scan."""
        ...

    def get_public_report(self, public_id: str) -> PublicReportResponse:
        """Return reduced public view for a public_id."""
        ...
