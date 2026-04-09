from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_scan_workflow
from app.schemas.api_contracts import PublicReportResponse
from app.services.ports import ScanWorkflowPort

router = APIRouter(tags=["public-reports"])


@router.get("/public-reports/{public_id}", response_model=PublicReportResponse)
def get_public_report(
    public_id: str,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
) -> PublicReportResponse:
    try:
        return workflow.get_public_report(public_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public report not found",
        ) from None
