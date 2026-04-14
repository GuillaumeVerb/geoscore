from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_scan_workflow
from app.schemas.api_contracts import (
    PageTypeOverrideRequest,
    PublicReportCreatedResponse,
    RescanResponse,
    ScanCompareResponse,
    ScanCreateRequest,
    ScanDetailResponse,
    ScanResponse,
    ScansListResponse,
    UserSummary,
)
from app.services.ports import ScanWorkflowPort

router = APIRouter(tags=["scans"])


def _not_found_scan() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")


@router.get("/scans", response_model=ScansListResponse)
def list_scans(
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
    user: Annotated[UserSummary, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=100, description="Max rows, newest first")] = 40,
    project_id: Annotated[UUID | None, Query(description="Filter scans assigned to this project")] = None,
) -> ScansListResponse:
    return workflow.list_recent_scans(limit=limit, user_id=user.id, project_id=project_id)


@router.post("/scans", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
def create_scan(
    body: ScanCreateRequest,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
    user: Annotated[UserSummary, Depends(get_current_user)],
) -> ScanResponse:
    try:
        return workflow.create_scan(body, user_id=user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/scans/{scan_id}/compare", response_model=ScanCompareResponse)
def compare_scan(
    scan_id: UUID,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
    user: Annotated[UserSummary, Depends(get_current_user)],
) -> ScanCompareResponse:
    """Compare a child scan to its parent (rescan lineage). `scan_id` must be the newer scan."""
    try:
        return workflow.get_scan_compare(scan_id, user_id=user.id)
    except KeyError:
        raise _not_found_scan() from None


@router.get("/scans/{scan_id}", response_model=ScanDetailResponse)
def get_scan(
    scan_id: UUID,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
    user: Annotated[UserSummary, Depends(get_current_user)],
) -> ScanDetailResponse:
    try:
        return workflow.get_scan(scan_id, user_id=user.id)
    except KeyError:
        raise _not_found_scan() from None


@router.post("/scans/{scan_id}/rescan", response_model=RescanResponse, status_code=status.HTTP_201_CREATED)
def rescan(
    scan_id: UUID,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
    user: Annotated[UserSummary, Depends(get_current_user)],
) -> RescanResponse:
    try:
        return workflow.rescan_scan(scan_id, user_id=user.id)
    except KeyError:
        raise _not_found_scan() from None


@router.patch("/scans/{scan_id}/page-type", response_model=ScanDetailResponse)
def patch_page_type(
    scan_id: UUID,
    body: PageTypeOverrideRequest,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
    user: Annotated[UserSummary, Depends(get_current_user)],
) -> ScanDetailResponse:
    try:
        return workflow.override_page_type(scan_id, body, user_id=user.id)
    except KeyError:
        raise _not_found_scan() from None


@router.post(
    "/scans/{scan_id}/public-report",
    response_model=PublicReportCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_public_report(
    scan_id: UUID,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
    user: Annotated[UserSummary, Depends(get_current_user)],
) -> PublicReportCreatedResponse:
    try:
        return workflow.create_public_report(scan_id, user_id=user.id)
    except KeyError:
        raise _not_found_scan() from None
