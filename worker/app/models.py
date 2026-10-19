"""
Standalone re-definitions of database models for the worker.
This avoids needing to mount the backend code inside the worker.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSON


class ScanJob(SQLModel, table=True):
    __tablename__ = "scan_jobs"

    id: uuid.UUID = Field(primary_key=True)
    project_id: uuid.UUID = Field(index=True)
    status: str = Field(max_length=50)
    phase: str = Field(max_length=50)
    progress: int = Field(default=0)
    ai_enabled: bool = Field(default=False)
    safety_profile: str = Field(default="standard", max_length=50)
    options_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    roe_confirmed: bool = Field(default=False)
    roe_confirmed_at: Optional[datetime] = Field(default=None)
    dry_run: bool = Field(default=False)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))


class ScanEvent(SQLModel, table=True):
    __tablename__ = "scan_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    scan_id: uuid.UUID = Field(index=True)
    level: str = Field(default="info", max_length=20)
    phase: str = Field(max_length=50)
    message: str = Field(sa_column=Column(Text))
    data_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Project(SQLModel, table=True):
    __tablename__ = "projects"
    
    id: uuid.UUID = Field(primary_key=True)
    name: str
    base_url: str
    environment_type: str = Field(default="local")
    mode: str = Field(default="grey_box")


class TargetConfig(SQLModel, table=True):
    __tablename__ = "target_configs"
    
    id: uuid.UUID = Field(primary_key=True)
    project_id: uuid.UUID = Field(index=True)
    allowed_hosts: list[str] = Field(sa_column=Column(JSON))
    allowed_paths: list[str] = Field(sa_column=Column(JSON))
    forbidden_paths: list[str] = Field(default=[], sa_column=Column(JSON))
    max_requests_per_second: int = Field(default=5)
    max_total_requests: int = Field(default=1000)
    allow_destructive_tests: bool = Field(default=False)
    allow_delete_requests: bool = Field(default=False)
    allow_payment_tests: bool = Field(default=False)
    selected_wordlist: Optional[str] = Field(default=None)


class Endpoint(SQLModel, table=True):
    __tablename__ = "endpoints"
    
    id: uuid.UUID = Field(primary_key=True)
    project_id: uuid.UUID = Field(index=True)
    method: str
    path: str
    tags: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    parameters_json: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    request_schema_json: Optional[Any] = Field(default=None, sa_column=Column(JSON))


class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    
    id: uuid.UUID = Field(primary_key=True)
    project_id: uuid.UUID = Field(index=True)
    role_id: Optional[uuid.UUID] = Field(default=None)
    label: str
    username: Optional[str] = None
    encrypted_secret: Optional[str] = None


class AuthConfig(SQLModel, table=True):
    __tablename__ = "auth_configs"
    
    id: uuid.UUID = Field(primary_key=True)
    project_id: uuid.UUID = Field(index=True)
    auth_type: str
    method: str
    header_template: str
    login_endpoint: Optional[str] = None
    username_field: str = "email"
    password_field: str = "password"
    token_json_path: str = "access_token"


class AuthSession(SQLModel, table=True):
    __tablename__ = "auth_sessions"
    
    id: uuid.UUID = Field(primary_key=True)
    account_id: uuid.UUID = Field(index=True)
    masked_token: Optional[str] = None


class TestCase(SQLModel, table=True):
    __tablename__ = "test_cases"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    scan_id: uuid.UUID = Field(index=True)
    project_id: uuid.UUID = Field(index=True)
    endpoint_id: Optional[uuid.UUID] = Field(default=None, index=True)
    attacker_account_id: Optional[uuid.UUID] = Field(default=None)
    victim_account_id: Optional[uuid.UUID] = Field(default=None)
    category: str = Field(max_length=100)
    name: str = Field(max_length=255)
    status: str = Field(default="generated", max_length=50)
    expected_secure_result: Optional[str] = Field(default=None, max_length=255)
    request_template_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TestExecution(SQLModel, table=True):
    __tablename__ = "test_executions"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    test_case_id: uuid.UUID = Field(index=True)
    scan_id: uuid.UUID = Field(index=True)
    status_code: Optional[int] = Field(default=None)
    duration_ms: Optional[int] = Field(default=None)
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    request_json_redacted: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    response_json_redacted: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Finding(SQLModel, table=True):
    __tablename__ = "findings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(index=True)
    scan_id: uuid.UUID = Field(index=True)
    test_case_id: uuid.UUID = Field(index=True)
    title: str = Field(max_length=255)
    category: str = Field(max_length=100)
    severity: str = Field(max_length=50)
    confidence: str = Field(max_length=50)
    endpoint_method: str = Field(max_length=20)
    endpoint_path: str = Field(max_length=255)
    attacker_role: Optional[str] = Field(default=None, max_length=100)
    victim_role: Optional[str] = Field(default=None, max_length=100)
    status: str = Field(default="open", max_length=50)
    description: str = Field(sa_column=Column(Text))
    impact: str = Field(sa_column=Column(Text))
    remediation: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Evidence(SQLModel, table=True):
    __tablename__ = "evidence"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    finding_id: uuid.UUID = Field(index=True, unique=True)
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
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- AI Planner Schemas ---
from pydantic import BaseModel
from typing import List, Optional

class EndpointClassification(BaseModel):
    business_area: str
    sensitivity: str
    possible_vulnerabilities: List[str]
    sensitive_fields: List[str]
    reasoning_summary: str

class TestCaseSuggestion(BaseModel):
    name: str
    category: str
    endpoint_method: str
    endpoint_path: str
    attacker_role: str
    victim_role: Optional[str] = None
    mutation_strategy: str
    expected_secure_result: str
    safety_notes: str

class PayloadMutationSuggestion(BaseModel):
    field: str
    mutation_values: List[str]
    reason: str
    risk_level: str

class FindingExplanation(BaseModel):
    summary: str
    impact: str
    remediation: str
    reproduction_steps: str



