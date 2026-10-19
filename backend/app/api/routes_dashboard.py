from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

from app.db.session import get_session
from app.models.project import Project
from app.models.scan_models import ScanJob
from app.models.finding_models import Finding

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

class ProjectSummary(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    description: Optional[str] = None

class FindingSummary(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    severity: str
    category: str
    created_at: datetime

class DashboardStats(BaseModel):
    total_projects: int
    active_scans: int
    high_severity_findings: int
    total_findings: int
    recent_projects: List[ProjectSummary]
    recent_findings: List[FindingSummary]

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(session: Session = Depends(get_session)):
    # Counts
    total_projects = session.exec(select(func.count(Project.id))).one()
    active_scans = session.exec(
        select(func.count(ScanJob.id)).where(ScanJob.status.in_(["pending", "running", "executing", "created", "loading"]))
    ).one()
    high_severity_findings = session.exec(
        select(func.count(Finding.id)).where(Finding.severity.in_(["high", "critical", "High", "Critical"]))
    ).one()
    total_findings = session.exec(select(func.count(Finding.id))).one()

    # Recent lists
    recent_projects_db = session.exec(
        select(Project).order_by(Project.created_at.desc()).limit(5)
    ).all()
    
    recent_findings_db = session.exec(
        select(Finding).order_by(Finding.created_at.desc()).limit(5)
    ).all()

    return DashboardStats(
        total_projects=total_projects,
        active_scans=active_scans,
        high_severity_findings=high_severity_findings,
        total_findings=total_findings,
        recent_projects=[
            ProjectSummary(
                id=p.id, name=p.name, created_at=p.created_at, description=p.description
            ) for p in recent_projects_db
        ],
        recent_findings=[
            FindingSummary(
                id=f.id, project_id=f.project_id, title=f.title, 
                severity=f.severity, category=f.category, created_at=f.created_at
            ) for f in recent_findings_db
        ]
    )
