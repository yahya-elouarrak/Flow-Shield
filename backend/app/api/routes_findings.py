from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
import uuid

from app.db.session import get_session
from app.models.finding_models import Finding, Evidence, FindingUpdate

router = APIRouter(prefix="", tags=["findings"])


@router.get("/projects/{project_id}/findings", response_model=List[Finding])
def get_project_findings(project_id: uuid.UUID, session: Session = Depends(get_session)):
    """List all findings for a project, ordered by newest first."""
    statement = select(Finding).where(Finding.project_id == project_id).order_by(Finding.created_at.desc())
    findings = session.exec(statement).all()
    return findings


@router.get("/findings/{finding_id}")
def get_finding_detail(finding_id: uuid.UUID, session: Session = Depends(get_session)):
    """Get a specific finding with its evidence attached."""
    finding = session.get(Finding, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
        
    return {
        **finding.model_dump(),
        "evidence": finding.evidence.model_dump() if finding.evidence else None
    }


@router.patch("/findings/{finding_id}/status", response_model=Finding)
def update_finding_status(finding_id: uuid.UUID, update_data: FindingUpdate, session: Session = Depends(get_session)):
    """Update the status of a finding (e.g. to false_positive)."""
    finding = session.get(Finding, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
        
    finding.status = update_data.status
    session.add(finding)
    session.commit()
    session.refresh(finding)
    return finding
