import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSON

from .base import TimestampMixin


# ─── UploadedSpec ────────────────────────────────────────────────────────────

class UploadedSpecBase(SQLModel):
    source_type: str = Field(max_length=10)  # "file" or "url"
    original_filename: Optional[str] = Field(default=None)
    source_url: Optional[str] = Field(default=None)
    parsed_successfully: bool = Field(default=False)
    parse_error: Optional[str] = Field(default=None, sa_column=Column(Text))


class UploadedSpec(UploadedSpecBase, table=True):
    __tablename__ = "uploaded_specs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    raw_spec_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    endpoints: List["Endpoint"] = Relationship(
        back_populates="spec",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class UploadedSpecRead(UploadedSpecBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: Optional[datetime]


# ─── Endpoint ────────────────────────────────────────────────────────────────

class EndpointBase(SQLModel):
    method: str
    path: str
    operation_id: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    auth_required: bool = Field(default=False)
    sensitive_score: int = Field(default=0)


class Endpoint(EndpointBase, table=True):
    __tablename__ = "endpoints"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    spec_id: uuid.UUID = Field(foreign_key="uploaded_specs.id", index=True)

    tags: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    parameters_json: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    request_schema_json: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    response_schema_json: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    path_params: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    query_params: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    body_fields: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    sensitive_reasons: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    spec: Optional[UploadedSpec] = Relationship(back_populates="endpoints")


class EndpointRead(EndpointBase):
    id: uuid.UUID
    project_id: uuid.UUID
    spec_id: uuid.UUID
    tags: Optional[List[str]] = []
    path_params: Optional[List[str]] = []
    query_params: Optional[List[str]] = []
    body_fields: Optional[List[str]] = []
    sensitive_reasons: Optional[List[str]] = []
    created_at: Optional[datetime]


class EndpointDetail(EndpointRead):
    """Extended read schema that includes the raw JSON fields."""
    parameters_json: Optional[Any] = None
    request_schema_json: Optional[Any] = None
    response_schema_json: Optional[Any] = None
