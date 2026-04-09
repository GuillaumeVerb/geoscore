from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_scan_workflow
from app.schemas.api_contracts import (
    PageTypeOverrideRequest,
    PublicReportCreatedResponse,
    RescanResponse,
    ScanCreateRequest,
    ScanDetailResponse,
    ScanResponse,
)
from app.services.ports import ScanWorkflowPort

router = APIRouter(tags=["scans"])


def _not_found_scan() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")


@router.post("/scans", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
def create_scan(
    body: ScanCreateRequest,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
) -> ScanResponse:
    return workflow.create_scan(body)


@router.get("/scans/{scan_id}", response_model=ScanDetailResponse)
def get_scan(
    scan_id: UUID,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
) -> ScanDetailResponse:
    try:
        return workflow.get_scan(scan_id)
    except KeyError:
        raise _not_found_scan() from None


@router.post("/scans/{scan_id}/rescan", response_model=RescanResponse, status_code=status.HTTP_201_CREATED)
def rescan(
    scan_id: UUID,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
) -> RescanResponse:
    try:
        return workflow.rescan_scan(scan_id)
    except KeyError:
        raise _not_found_scan() from None


@router.patch("/scans/{scan_id}/page-type", response_model=ScanDetailResponse)
def patch_page_type(
    scan_id: UUID,
    body: PageTypeOverrideRequest,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
) -> ScanDetailResponse:
    try:
        return workflow.override_page_type(scan_id, body)
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
) -> PublicReportCreatedResponse:
    try:
        return workflow.create_public_report(scan_id)
    except KeyError:
        raise _not_found_scan() from None
