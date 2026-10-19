import uuid
from enum import Enum
from typing import Optional, List, Any
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy.dialects.postgresql import JSON
from pydantic import HttpUrl, AnyHttpUrl

from .base import TimestampMixin

class EnvironmentType(str, Enum):
    local = "local"
    lab = "lab"
    staging = "staging"
    bug_bounty = "bug_bounty"

class TargetConfigBase(SQLModel):
    allowed_hosts: List[str] = Field(default=[], sa_column=Column(JSON))
    allowed_paths: List[str] = Field(default=[], sa_column=Column(JSON))
    forbidden_paths: List[str] = Field(default=[], sa_column=Column(JSON))
    max_requests_per_second: int = Field(default=5)
    max_total_requests: int = Field(default=1000)
    allow_destructive_tests: bool = Field(default=False)
    allow_delete_requests: bool = Field(default=False)
    allow_payment_tests: bool = Field(default=False)
    selected_wordlist: Optional[str] = Field(default=None)

class TargetConfig(TargetConfigBase, SQLModel, table=True):
    __tablename__ = "target_configs"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", unique=True)
    
    project: "Project" = Relationship(back_populates="target_config")

class TargetConfigRead(TargetConfigBase):
    id: uuid.UUID
    project_id: uuid.UUID

class TargetConfigUpdate(SQLModel):
    allowed_hosts: Optional[List[str]] = None
    allowed_paths: Optional[List[str]] = None
    forbidden_paths: Optional[List[str]] = None
    max_requests_per_second: Optional[int] = None
    max_total_requests: Optional[int] = None
    allow_destructive_tests: Optional[bool] = None
    allow_delete_requests: Optional[bool] = None
    allow_payment_tests: Optional[bool] = None
    selected_wordlist: Optional[str] = None

class ProjectBase(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    base_url: str
    environment_type: EnvironmentType = Field(default=EnvironmentType.local)
    mode: str = Field(default="grey_box")

class Project(ProjectBase, TimestampMixin, table=True):
    __tablename__ = "projects"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    target_config: Optional[TargetConfig] = Relationship(
        back_populates="project", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase, TimestampMixin):
    id: uuid.UUID

class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_url: Optional[str] = None
    environment_type: Optional[EnvironmentType] = None
    mode: Optional[str] = None
