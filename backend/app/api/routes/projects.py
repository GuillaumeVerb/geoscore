from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_scan_workflow
from app.schemas.api_contracts import UserSummary
from app.schemas.project import ProjectCreateRequest, ProjectRead, ProjectsListResponse
from app.services.ports import ScanWorkflowPort

router = APIRouter(tags=["projects"])


@router.get("/projects", response_model=ProjectsListResponse)
def list_projects(
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
    user: Annotated[UserSummary, Depends(get_current_user)],
) -> ProjectsListResponse:
    return workflow.list_projects(user_id=user.id)


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreateRequest,
    workflow: Annotated[ScanWorkflowPort, Depends(get_scan_workflow)],
    user: Annotated[UserSummary, Depends(get_current_user)],
) -> ProjectRead:
    return workflow.create_project(body, user_id=user.id)
