import uuid
from typing import List
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlmodel import Session, select
from pydantic import BaseModel

from app.db.session import get_session
from app.models.project import Project
from app.models.openapi import (
    UploadedSpec, UploadedSpecRead,
    Endpoint, EndpointRead, EndpointDetail,
)
from app.services.openapi_parser import parse_openapi_spec

router = APIRouter(prefix="/projects/{project_id}/openapi", tags=["openapi"])


# ─── Request schemas ─────────────────────────────────────────────────────────

class ImportUrlRequest(BaseModel):
    url: str


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _validate_url(url: str, project: Project) -> str:
    """Basic URL validation. For MVP, allow localhost and project base_url host."""
    try:
        parsed = urlparse(url)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL format.")

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http and https schemes are allowed.")

    hostname = parsed.hostname or ""

    # Always allow localhost / loopback for local development
    allowed_hosts = {"localhost", "127.0.0.1", "host.docker.internal"}

    # Allow the project's configured base_url host
    try:
        project_host = urlparse(project.base_url).hostname
        if project_host:
            allowed_hosts.add(project_host)
    except Exception:
        pass

    # Allow docker-compose service names
    allowed_hosts.add("vulnerable-saas")
    allowed_hosts.add("backend")
    
    # Allow GitHub for official demo specs
    allowed_hosts.add("raw.githubusercontent.com")

    if hostname not in allowed_hosts:
        raise HTTPException(
            status_code=400,
            detail=f"Host '{hostname}' is not in the allowed list. "
                   f"Allowed: {', '.join(sorted(allowed_hosts))}",
        )

    return url


def _get_project(session: Session, project_id: uuid.UUID) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _clear_existing(session: Session, project_id: uuid.UUID) -> None:
    """Delete all existing specs and endpoints for a project (replace mode)."""
    old_specs = session.exec(
        select(UploadedSpec).where(UploadedSpec.project_id == project_id)
    ).all()
    for spec in old_specs:
        session.delete(spec)
    session.flush()


def _store_parsed(
    session: Session,
    project_id: uuid.UUID,
    spec_record: UploadedSpec,
    parsed_endpoints: list,
) -> UploadedSpec:
    """Store the spec and its endpoints in the database."""
    session.add(spec_record)
    session.flush()

    for ep_data in parsed_endpoints:
        endpoint = Endpoint(
            project_id=project_id,
            spec_id=spec_record.id,
            **ep_data,
        )
        session.add(endpoint)

    session.commit()
    session.refresh(spec_record)
    return spec_record


# ─── Import from URL ─────────────────────────────────────────────────────────

@router.post("/import-url", response_model=UploadedSpecRead, status_code=status.HTTP_201_CREATED)
def import_from_url(
    *,
    session: Session = Depends(get_session),
    project_id: uuid.UUID,
    body: ImportUrlRequest,
):
    project = _get_project(session, project_id)
    url = _validate_url(body.url, project)
    
    # QA Demo Fix: Rewrite localhost to vulnerable-saas for docker-internal communication
    if "localhost:9000" in url or "127.0.0.1:9000" in url:
        url = url.replace("localhost:9000", "vulnerable-saas:9000").replace("127.0.0.1:9000", "vulnerable-saas:9000")

    # Fetch the spec
    try:
        response = httpx.get(url, timeout=15.0, follow_redirects=True)
        response.raise_for_status()
        raw_content = response.text
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch spec: HTTP {e.response.status_code}",
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to connect to URL: {str(e)}",
        )

    # Parse
    spec_record = UploadedSpec(
        project_id=project_id,
        source_type="url",
        source_url=url,
    )

    try:
        spec_dict, endpoints = parse_openapi_spec(raw_content)
        spec_record.raw_spec_json = spec_dict
        spec_record.parsed_successfully = True
    except ValueError as e:
        spec_record.parsed_successfully = False
        spec_record.parse_error = str(e)
        session.add(spec_record)
        session.commit()
        session.refresh(spec_record)
        raise HTTPException(status_code=422, detail=f"Parse error: {e}")

    # Replace existing data and store
    _clear_existing(session, project_id)
    _store_parsed(session, project_id, spec_record, endpoints)

    return spec_record


# ─── Upload file ─────────────────────────────────────────────────────────────

@router.post("/upload", response_model=UploadedSpecRead, status_code=status.HTTP_201_CREATED)
async def upload_spec_file(
    *,
    session: Session = Depends(get_session),
    project_id: uuid.UUID,
    file: UploadFile = File(...),
):
    project = _get_project(session, project_id)

    # Read uploaded file content
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large (max 10MB).")

    raw_content = content.decode("utf-8", errors="replace")

    spec_record = UploadedSpec(
        project_id=project_id,
        source_type="file",
        original_filename=file.filename,
    )

    try:
        spec_dict, endpoints = parse_openapi_spec(raw_content)
        spec_record.raw_spec_json = spec_dict
        spec_record.parsed_successfully = True
    except ValueError as e:
        spec_record.parsed_successfully = False
        spec_record.parse_error = str(e)
        session.add(spec_record)
        session.commit()
        session.refresh(spec_record)
        raise HTTPException(status_code=422, detail=f"Parse error: {e}")

    _clear_existing(session, project_id)
    _store_parsed(session, project_id, spec_record, endpoints)

    return spec_record


# ─── Read endpoints ──────────────────────────────────────────────────────────

@router.get("/endpoints", response_model=List[EndpointRead])
def list_endpoints(
    *,
    session: Session = Depends(get_session),
    project_id: uuid.UUID,
    skip: int = 0,
    limit: int = 500,
):
    _get_project(session, project_id)
    stmt = (
        select(Endpoint)
        .where(Endpoint.project_id == project_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(stmt).all()


@router.get("/endpoints/{endpoint_id}", response_model=EndpointDetail)
def read_endpoint(
    *,
    session: Session = Depends(get_session),
    project_id: uuid.UUID,
    endpoint_id: uuid.UUID,
):
    _get_project(session, project_id)
    endpoint = session.get(Endpoint, endpoint_id)
    if not endpoint or endpoint.project_id != project_id:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoint


# ─── Delete all endpoints ────────────────────────────────────────────────────

@router.delete("/endpoints", status_code=status.HTTP_200_OK)
def delete_all_endpoints(
    *,
    session: Session = Depends(get_session),
    project_id: uuid.UUID,
):
    _get_project(session, project_id)
    _clear_existing(session, project_id)
    session.commit()
    return {"ok": True, "detail": "All endpoints and specs removed."}
