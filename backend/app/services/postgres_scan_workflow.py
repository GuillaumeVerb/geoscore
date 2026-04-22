"""Postgres-backed scan workflow: persists scans and runs the real pipeline (no LLM)."""

from __future__ import annotations

import secrets
from uuid import UUID

from sqlalchemy import desc, select

from app.core.url_norm import normalize_submitted_url
from app.db.session import SessionLocal
from app.domain.enums import ScanStatus
from app.models.project import Project
from app.models.public_report import PublicReport
from app.models.scan import Scan
from app.models.scan_extraction import ScanExtraction
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
from app.services.pipeline.orchestrator import rescore_scan_only, schedule_scan_pipeline
from app.services.scan_compare import build_scan_compare
from app.services.scan_create_rate_limit import check_scan_create_rate_limit
from app.services.scan_detail import list_scan_summaries, public_report_to_response, scan_to_detail_response


class PostgresScanWorkflow:
    def create_scan(self, body: ScanCreateRequest, *, user_id: UUID) -> ScanResponse:
        check_scan_create_rate_limit(user_id)
        raw = str(body.url).strip()
        normalized_url, domain, path = normalize_submitted_url(raw)
        db = SessionLocal()
        try:
            if body.project_id is not None:
                proj = db.get(Project, body.project_id)
                if proj is None or proj.user_id != user_id:
                    raise ValueError("Invalid or inaccessible project")
            scan = Scan(
                user_id=user_id,
                submitted_url=raw,
                normalized_url=normalized_url,
                domain=domain,
                path=path,
                status=ScanStatus.QUEUED.value,
                project_id=body.project_id,
                page_type_final=body.page_type_override.value if body.page_type_override else None,
            )
            db.add(scan)
            db.commit()
            db.refresh(scan)
            scan_id = scan.id
        finally:
            db.close()

        schedule_scan_pipeline(scan_id)
        return ScanResponse(
            scan_id=scan_id,
            status=ScanStatus.QUEUED,
            submitted_url=raw,
            normalized_url=normalized_url,
        )

    def get_scan(self, scan_id: UUID, *, user_id: UUID) -> ScanDetailResponse:
        db = SessionLocal()
        try:
            parent = db.get(Scan, scan_id)
            if parent is None or parent.user_id != user_id:
                raise KeyError(scan_id)
            detail = scan_to_detail_response(db, scan_id)
            if detail is None:
                raise KeyError(scan_id)
            return detail
        finally:
            db.close()

    def list_recent_scans(
        self, limit: int = 40, *, user_id: UUID, project_id: UUID | None = None
    ) -> ScansListResponse:
        db = SessionLocal()
        try:
            rows = list_scan_summaries(db, user_id=user_id, limit=limit, project_id=project_id)
            return ScansListResponse(scans=rows)
        finally:
            db.close()

    def list_projects(self, *, user_id: UUID) -> ProjectsListResponse:
        db = SessionLocal()
        try:
            rows = db.scalars(select(Project).where(Project.user_id == user_id).order_by(desc(Project.created_at))).all()
            items = [
                ProjectRead(id=r.id, user_id=r.user_id, name=r.name, created_at=r.created_at) for r in rows
            ]
            return ProjectsListResponse(projects=items)
        finally:
            db.close()

    def create_project(self, body: ProjectCreateRequest, *, user_id: UUID) -> ProjectRead:
        db = SessionLocal()
        try:
            row = Project(user_id=user_id, name=body.name.strip())
            db.add(row)
            db.commit()
            db.refresh(row)
            return ProjectRead(id=row.id, user_id=row.user_id, name=row.name, created_at=row.created_at)
        finally:
            db.close()

    def get_scan_compare(self, scan_id: UUID, *, user_id: UUID) -> ScanCompareResponse:
        db = SessionLocal()
        try:
            child = db.get(Scan, scan_id)
            if child is None or child.user_id != user_id or child.parent_scan_id is None:
                raise KeyError(scan_id)
            parent = db.get(Scan, child.parent_scan_id)
            if parent is None or parent.user_id != user_id:
                raise KeyError(scan_id)
            d_parent = scan_to_detail_response(db, parent.id)
            d_child = scan_to_detail_response(db, child.id)
            if d_parent is None or d_child is None:
                raise KeyError(scan_id)
            return build_scan_compare(d_parent, d_child)
        finally:
            db.close()

    def rescan_scan(self, scan_id: UUID, *, user_id: UUID) -> RescanResponse:
        check_scan_create_rate_limit(user_id)
        db = SessionLocal()
        try:
            parent = db.get(Scan, scan_id)
            if parent is None or parent.user_id != user_id:
                raise KeyError(scan_id)
            child = Scan(
                user_id=parent.user_id,
                project_id=parent.project_id,
                parent_scan_id=parent.id,
                submitted_url=parent.submitted_url,
                normalized_url=parent.normalized_url,
                domain=parent.domain,
                path=parent.path,
                status=ScanStatus.QUEUED.value,
                analysis_mode=parent.analysis_mode,
                scan_trigger=parent.scan_trigger,
                page_type_final=parent.page_type_final,
            )
            db.add(child)
            db.commit()
            db.refresh(child)
            new_id = child.id
            parent_id = parent.id
        finally:
            db.close()

        schedule_scan_pipeline(new_id)
        return RescanResponse(scan_id=new_id, parent_scan_id=parent_id, status=ScanStatus.QUEUED)

    def override_page_type(self, scan_id: UUID, body: PageTypeOverrideRequest, *, user_id: UUID) -> ScanDetailResponse:
        db = SessionLocal()
        try:
            scan = db.get(Scan, scan_id)
            if scan is None or scan.user_id != user_id:
                raise KeyError(scan_id)
            scan.page_type_final = body.page_type.value
            has_extraction = (
                db.execute(select(ScanExtraction.id).where(ScanExtraction.scan_id == scan_id).limit(1)).first()
                is not None
            )
            if has_extraction:
                rescore_scan_only(db, scan_id)
            db.commit()
            detail = scan_to_detail_response(db, scan_id)
            if detail is None:
                raise KeyError(scan_id)
            return detail
        finally:
            db.close()

    def create_public_report(self, scan_id: UUID, *, user_id: UUID) -> PublicReportCreatedResponse:
        db = SessionLocal()
        try:
            scan = db.get(Scan, scan_id)
            if scan is None or scan.user_id != user_id:
                raise KeyError(scan_id)
            public_id = secrets.token_urlsafe(12)
            db.add(PublicReport(scan_id=scan.id, public_id=public_id, is_enabled=True))
            db.commit()
            return PublicReportCreatedResponse(public_id=public_id, url_path=f"/report/{public_id}")
        finally:
            db.close()

    def get_public_report(self, public_id: str) -> PublicReportResponse:
        db = SessionLocal()
        try:
            out = public_report_to_response(db, public_id)
            if out is None:
                raise KeyError(public_id)
            return out
        finally:
            db.close()


postgres_scan_workflow = PostgresScanWorkflow()
