"""
API routes for scan jobs and scan events.
"""

import uuid
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.project import Project, TargetConfig
from app.models.openapi import Endpoint
from app.models.scan_models import (
    ScanJob, ScanJobCreate, ScanJobRead,
    ScanEvent, ScanEventRead
)

router = APIRouter(tags=["scans"])


def _get_project(session: Session, project_id: uuid.UUID) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/{project_id}/scans", response_model=ScanJobRead, status_code=status.HTTP_201_CREATED,
             summary="Create a new scan job")
def create_scan(
    *, session: Session = Depends(get_session),
    project_id: uuid.UUID, body: ScanJobCreate,
):
    project = _get_project(session, project_id)

    # 1. Validate Rules of Engagement
    if not body.roe_confirmed:
        raise HTTPException(
            status_code=400,
            detail="You must confirm the Rules of Engagement to launch a scan."
        )

    # 2. Check for Target Config (Safety Profile)
    stmt = select(TargetConfig).where(TargetConfig.project_id == project_id)
    target_config = session.exec(stmt).first()
    if not target_config:
        # Create a default one if none exists (for MVP convenience)
        target_config = TargetConfig(
            project_id=project_id,
            allowed_hosts=[project.base_url.split("//")[-1].split(":")[0]],
            allowed_paths=["/*"],
        )
        session.add(target_config)
        session.commit()
        session.refresh(target_config)

    # 3. Check for Endpoints
    stmt = select(Endpoint).where(Endpoint.project_id == project_id)
    endpoint_count = len(session.exec(stmt).all())
    if endpoint_count == 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot launch scan: No endpoints found. Please import an OpenAPI spec first."
        )

    scan_job = ScanJob(
        project_id=project_id,
        ai_enabled=body.ai_enabled,
        safety_profile=body.safety_profile,
        options_json=body.options_json,
        roe_confirmed=body.roe_confirmed,
        roe_confirmed_at=datetime.now(timezone.utc),
        status="pending",
        phase="created",
    )
    session.add(scan_job)
    session.commit()
    session.refresh(scan_job)
    
    # Add initial event
    event = ScanEvent(
        scan_id=scan_job.id,
        phase="created",
        message="Scan job created and pending pickup by worker.",
    )
    session.add(event)
    session.commit()
    
    return scan_job


@router.get("/projects/{project_id}/scans", response_model=List[ScanJobRead],
            summary="List scan jobs for a project")
def list_scans(
    *, session: Session = Depends(get_session), project_id: uuid.UUID,
):
    _get_project(session, project_id)
    stmt = select(ScanJob).where(ScanJob.project_id == project_id).order_by(ScanJob.created_at.desc())
    return session.exec(stmt).all()


@router.get("/scans/{scan_id}", response_model=ScanJobRead,
            summary="Get a specific scan job")
def get_scan(
    *, session: Session = Depends(get_session), scan_id: uuid.UUID,
):
    scan_job = session.get(ScanJob, scan_id)
    if not scan_job:
        raise HTTPException(status_code=404, detail="Scan job not found")
    return scan_job


@router.get("/scans/{scan_id}/events", response_model=List[ScanEventRead],
            summary="Get events for a specific scan job")
def get_scan_events(
    *, session: Session = Depends(get_session), scan_id: uuid.UUID,
):
    scan_job = session.get(ScanJob, scan_id)
    if not scan_job:
        raise HTTPException(status_code=404, detail="Scan job not found")
        
    stmt = select(ScanEvent).where(ScanEvent.scan_id == scan_id).order_by(ScanEvent.created_at)
    return session.exec(stmt).all()


@router.post("/scans/{scan_id}/cancel", response_model=ScanJobRead,
             summary="Cancel a pending or running scan job")
def cancel_scan(
    *, session: Session = Depends(get_session), scan_id: uuid.UUID,
):
    scan_job = session.get(ScanJob, scan_id)
    if not scan_job:
        raise HTTPException(status_code=404, detail="Scan job not found")
        
    if scan_job.status in ["completed", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel scan in status: {scan_job.status}")
        
    scan_job.status = "cancelled"
    
    event = ScanEvent(
        scan_id=scan_job.id,
        level="warning",
        phase=scan_job.phase,
        message="Scan cancelled by user.",
    )
    session.add(event)
    session.add(scan_job)
    session.commit()
    session.refresh(scan_job)
    return scan_job
