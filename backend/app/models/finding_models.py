import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSON


class FindingBase(SQLModel):
    title: str = Field(max_length=255)
    category: str = Field(max_length=100) # BOLA, BFLA, MASS_ASSIGNMENT, etc.
    severity: str = Field(max_length=50) # critical, high, medium, low, info
    confidence: str = Field(max_length=50) # confirmed, likely, suspicious
    endpoint_method: str = Field(max_length=20)
    endpoint_path: str = Field(max_length=255)
    attacker_role: Optional[str] = Field(default=None, max_length=100)
    victim_role: Optional[str] = Field(default=None, max_length=100)
    status: str = Field(default="open", max_length=50) # open, accepted, false_positive, fixed
    description: str = Field(sa_column=Column(Text))
    impact: str = Field(sa_column=Column(Text))
    remediation: str = Field(sa_column=Column(Text))


class Finding(FindingBase, table=True):
    __tablename__ = "findings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    scan_id: uuid.UUID = Field(foreign_key="scan_jobs.id", index=True)
    test_case_id: uuid.UUID = Field(foreign_key="test_cases.id", index=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    
    evidence: Optional["Evidence"] = Relationship(
        back_populates="finding",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False}
    )


class EvidenceBase(SQLModel):
    request_method: str = Field(max_length=20)
    request_url: str = Field(max_length=2048)
    request_headers_redacted: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    request_body_redacted: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    response_status: int
    response_headers_redacted: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    response_body_redacted: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    proof_text: str = Field(sa_column=Column(Text))
    before_state_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    after_state_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class Evidence(EvidenceBase, table=True):
    __tablename__ = "evidence"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    finding_id: uuid.UUID = Field(foreign_key="findings.id", index=True, unique=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    
    finding: Optional[Finding] = Relationship(back_populates="evidence")


class FindingUpdate(SQLModel):
    status: str
