"""
Models for FlowShield scan jobs, events, and test cases.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSON

from .base import TimestampMixin


# ─── ScanJob ─────────────────────────────────────────────────────────────────

class ScanJobBase(SQLModel):
    status: str = Field(default="pending", max_length=50) # created, pending, running, completed, failed, cancelled
    phase: str = Field(default="created", max_length=50)  # created, loading, authenticating, planning, executing, verifying, reporting
    progress: int = Field(default=0)                      # 0-100
    ai_enabled: bool = Field(default=False)
    safety_profile: str = Field(default="standard", max_length=50)
    options_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    roe_confirmed: bool = Field(default=False)
    roe_confirmed_at: Optional[datetime] = Field(default=None)
    dry_run: bool = Field(default=False)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Counters
    endpoints_loaded: int = Field(default=0)
    accounts_authenticated: int = Field(default=0)
    tests_generated: int = Field(default=0)
    tests_executed: int = Field(default=0)
    requests_sent: int = Field(default=0)
    findings_confirmed: int = Field(default=0)
    evidence_records_created: int = Field(default=0)
    errors_count: int = Field(default=0)

class ScanJob(ScanJobBase, table=True):
    __tablename__ = "scan_jobs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    events: List["ScanEvent"] = Relationship(
        back_populates="scan",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "ScanEvent.created_at"},
    )
    test_cases: List["TestCase"] = Relationship(
        back_populates="scan",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ScanJobCreate(SQLModel):
    ai_enabled: bool = False
    safety_profile: str = "standard"
    options_json: Optional[Dict[str, Any]] = None
    roe_confirmed: bool = False
    dry_run: bool = False


class ScanJobRead(ScanJobBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: Optional[datetime]


# ─── ScanEvent ───────────────────────────────────────────────────────────────

class ScanEventBase(SQLModel):
    level: str = Field(default="info", max_length=20) # info, warning, error
    phase: str = Field(max_length=50)
    message: str = Field(sa_column=Column(Text))
    data_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class ScanEvent(ScanEventBase, table=True):
    __tablename__ = "scan_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    scan_id: uuid.UUID = Field(foreign_key="scan_jobs.id", index=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    scan: Optional[ScanJob] = Relationship(back_populates="events")


class ScanEventRead(ScanEventBase):
    id: uuid.UUID
    scan_id: uuid.UUID
    created_at: Optional[datetime]


# ─── TestCase ────────────────────────────────────────────────────────────────

class TestCaseBase(SQLModel):
    category: str = Field(max_length=100) # BOLA, BFLA, MASS_ASSIGNMENT
    name: str = Field(max_length=255)
    status: str = Field(default="generated", max_length=50) # generated, running, passed, failed, suspicious, error
    expected_secure_result: Optional[str] = Field(default=None, max_length=255)
    request_template_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class TestCase(TestCaseBase, table=True):
    __tablename__ = "test_cases"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    scan_id: uuid.UUID = Field(foreign_key="scan_jobs.id", index=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    endpoint_id: Optional[uuid.UUID] = Field(default=None, foreign_key="endpoints.id", index=True)
    attacker_account_id: Optional[uuid.UUID] = Field(default=None, foreign_key="accounts.id")
    victim_account_id: Optional[uuid.UUID] = Field(default=None, foreign_key="accounts.id")
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    scan: Optional[ScanJob] = Relationship(back_populates="test_cases")
    executions: List["TestExecution"] = Relationship(
        back_populates="test_case",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# ─── TestExecution ───────────────────────────────────────────────────────────

class TestExecutionBase(SQLModel):
    status_code: Optional[int] = Field(default=None)
    duration_ms: Optional[int] = Field(default=None)
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    request_json_redacted: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    request_headers_redacted: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    response_json_redacted: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    response_headers_redacted: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class TestExecution(TestExecutionBase, table=True):
    __tablename__ = "test_executions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    test_case_id: uuid.UUID = Field(foreign_key="test_cases.id", index=True)
    scan_id: uuid.UUID = Field(foreign_key="scan_jobs.id", index=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    test_case: Optional[TestCase] = Relationship(back_populates="executions")
