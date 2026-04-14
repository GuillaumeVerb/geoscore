"""In-memory mock implementation of ScanWorkflowPort — correctly shaped contracts, no Postgres."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from urllib.parse import urlparse
from uuid import UUID, uuid4

from app.core.url_norm import normalize_submitted_url
from app.domain.enums import AnalysisConfidence, PageType, ScanStatus
from app.schemas.api_contracts import (
    PageTypeOverrideRequest,
    PublicReportCreatedResponse,
    PublicReportResponse,
    RescanResponse,
    ScanCompareResponse,
    ScanCreateRequest,
    ScanDetailResponse,
    ScanResponse,
    ScanSummaryItem,
    ScansListResponse,
)
from app.schemas.project import ProjectCreateRequest, ProjectRead, ProjectsListResponse
from app.services.scan_compare import build_scan_compare


def _owner_from_meta(meta: dict | None) -> UUID | None:
    raw = (meta or {}).get("user_id")
    if raw is None:
        return None
    try:
        return UUID(str(raw))
    except ValueError:
        return None


class MockScanWorkflow:
    def __init__(self) -> None:
        self._by_id: dict[UUID, ScanDetailResponse] = {}
        self._public_to_scan: dict[str, UUID] = {}
        self._projects_by_user: dict[UUID, list[ProjectRead]] = {}

    def create_scan(self, body: ScanCreateRequest, *, user_id: UUID) -> ScanResponse:
        if body.project_id is not None:
            owned = self._projects_by_user.get(user_id, [])
            if not any(p.id == body.project_id for p in owned):
                raise ValueError("Invalid or inaccessible project")
        scan_id = uuid4()
        raw = str(body.url)
        normalized_url, _, _ = normalize_submitted_url(raw)
        created_at = datetime.now(timezone.utc)
        meta: dict = {
            "submitted_url": raw,
            "normalized_url": normalized_url,
            "scoring_version": None,
            "ruleset_version": None,
            "llm_prompt_version": None,
            "created_at": created_at.isoformat(),
            "user_id": str(user_id),
        }
        if body.project_id is not None:
            meta["project_id"] = str(body.project_id)
        detail = ScanDetailResponse(
            scan_id=scan_id,
            status=ScanStatus.QUEUED,
            page_type_detected=None,
            page_type_final=body.page_type_override,
            analysis_confidence=AnalysisConfidence.UNKNOWN,
            global_score=None,
            seo_score=None,
            geo_score=None,
            scores=None,
            strengths=[],
            issues=[],
            recommendations=[],
            limitations=[],
            summary=None,
            extraction=None,
            error_code=None,
            error_message=None,
            meta=meta,
        )
        self._by_id[scan_id] = detail
        return ScanResponse(
            scan_id=scan_id,
            status=ScanStatus.QUEUED,
            submitted_url=raw,
            normalized_url=normalized_url,
        )

    def get_scan(self, scan_id: UUID, *, user_id: UUID) -> ScanDetailResponse:
        detail = self._by_id.get(scan_id)
        owner = _owner_from_meta(detail.meta if detail else None)
        if detail is None or owner != user_id:
            raise KeyError(scan_id)
        return detail

    def list_recent_scans(
        self, limit: int = 40, *, user_id: UUID, project_id: UUID | None = None
    ) -> ScansListResponse:
        rows: list[tuple[UUID, ScanDetailResponse, datetime]] = []
        for sid, detail in self._by_id.items():
            if _owner_from_meta(detail.meta) != user_id:
                continue
            meta = detail.meta or {}
            if project_id is not None:
                raw_pid = meta.get("project_id")
                if raw_pid is None or UUID(str(raw_pid)) != project_id:
                    continue
            raw = meta.get("created_at")
            if raw:
                try:
                    ts = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
                except ValueError:
                    ts = datetime.min.replace(tzinfo=timezone.utc)
            else:
                ts = datetime.min.replace(tzinfo=timezone.utc)
            rows.append((sid, detail, ts))
        rows.sort(key=lambda x: x[2], reverse=True)
        items: list[ScanSummaryItem] = []
        for scan_id, detail, ts in rows[:limit]:
            meta = detail.meta or {}
            submitted = str(meta.get("submitted_url", ""))
            url_for_parse = submitted if submitted.startswith("http") else f"https://{submitted}"
            domain = urlparse(url_for_parse).hostname or submitted or "—"
            completed_raw = meta.get("completed_at")
            completed_at: datetime | None = None
            if completed_raw:
                try:
                    completed_at = datetime.fromisoformat(str(completed_raw).replace("Z", "+00:00"))
                except ValueError:
                    completed_at = None
            raw_pid = meta.get("project_id")
            proj_uuid = UUID(str(raw_pid)) if raw_pid else None
            raw_parent = meta.get("parent_scan_id")
            parent_uuid = UUID(str(raw_parent)) if raw_parent else None
            items.append(
                ScanSummaryItem(
                    scan_id=scan_id,
                    status=detail.status,
                    submitted_url=submitted,
                    domain=domain,
                    page_type_detected=detail.page_type_detected,
                    page_type_final=detail.page_type_final,
                    analysis_confidence=detail.analysis_confidence,
                    global_score=detail.global_score,
                    seo_score=detail.seo_score,
                    geo_score=detail.geo_score,
                    created_at=ts,
                    completed_at=completed_at,
                    project_id=proj_uuid,
                    parent_scan_id=parent_uuid,
                )
            )
        return ScansListResponse(scans=items)

    def list_projects(self, *, user_id: UUID) -> ProjectsListResponse:
        return ProjectsListResponse(projects=list(self._projects_by_user.get(user_id, [])))

    def create_project(self, body: ProjectCreateRequest, *, user_id: UUID) -> ProjectRead:
        pid = uuid4()
        now = datetime.now(timezone.utc)
        row = ProjectRead(id=pid, user_id=user_id, name=body.name.strip(), created_at=now)
        self._projects_by_user.setdefault(user_id, []).insert(0, row)
        return row

    def get_scan_compare(self, scan_id: UUID, *, user_id: UUID) -> ScanCompareResponse:
        child = self.get_scan(scan_id, user_id=user_id)
        parent_raw = (child.meta or {}).get("parent_scan_id")
        if not parent_raw:
            raise KeyError(scan_id)
        parent_id = UUID(str(parent_raw))
        parent = self.get_scan(parent_id, user_id=user_id)
        return build_scan_compare(parent, child)

    def rescan_scan(self, scan_id: UUID, *, user_id: UUID) -> RescanResponse:
        parent = self.get_scan(scan_id, user_id=user_id)
        new_id = uuid4()
        child_created = datetime.now(timezone.utc).isoformat()
        child = parent.model_copy(
            update={
                "scan_id": new_id,
                "status": ScanStatus.QUEUED,
                "global_score": None,
                "seo_score": None,
                "geo_score": None,
                "scores": None,
                "extraction": None,
                "issues": [],
                "recommendations": [],
                "strengths": [],
                "limitations": [],
                "summary": None,
                "analysis_confidence": AnalysisConfidence.UNKNOWN,
                "error_code": None,
                "error_message": None,
                "meta": {
                    **parent.meta,
                    "parent_scan_id": str(parent.scan_id),
                    "created_at": child_created,
                    "completed_at": None,
                },
            }
        )
        self._by_id[new_id] = child
        return RescanResponse(scan_id=new_id, parent_scan_id=parent.scan_id, status=ScanStatus.QUEUED)

    def override_page_type(self, scan_id: UUID, body: PageTypeOverrideRequest, *, user_id: UUID) -> ScanDetailResponse:
        cur = self._by_id[scan_id]
        updated = cur.model_copy(update={"page_type_final": body.page_type})
        self._by_id[scan_id] = updated
        return updated

    def create_public_report(self, scan_id: UUID, *, user_id: UUID) -> PublicReportCreatedResponse:
        _ = self.get_scan(scan_id, user_id=user_id)
        public_id = secrets.token_urlsafe(12)
        self._public_to_scan[public_id] = scan_id
        return PublicReportCreatedResponse(public_id=public_id, url_path=f"/report/{public_id}")

    def get_public_report(self, public_id: str) -> PublicReportResponse:
        scan_id = self._public_to_scan[public_id]
        d = self._by_id[scan_id]
        submitted = str(d.meta.get("submitted_url", ""))
        return PublicReportResponse(
            public_id=public_id,
            scan_id=d.scan_id,
            submitted_url=submitted,
            page_type=d.page_type_final or d.page_type_detected,
            analysis_confidence=d.analysis_confidence,
            global_score=d.global_score,
            seo_score=d.seo_score,
            geo_score=d.geo_score,
            scores=d.scores,
            top_issues=d.issues[:5],
            top_fixes=d.recommendations[:5],
            limitations=d.limitations,
            summary=d.summary,
            analyzed_at=d.meta.get("completed_at"),
            meta={
                k: v
                for k, v in d.meta.items()
                if k in ("scoring_version", "ruleset_version", "llm_prompt_version")
            },
        )


mock_scan_workflow = MockScanWorkflow()
