import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from urllib.parse import urlparse

from app.db.session import get_session
from app.models.project import (
    Project, ProjectRead, ProjectCreate, ProjectUpdate,
    TargetConfig, TargetConfigRead, TargetConfigUpdate
)

router = APIRouter(prefix="/projects", tags=["projects"])

def get_default_allowed_hosts(base_url: str) -> List[str]:
    try:
        parsed = urlparse(base_url)
        if parsed.hostname:
            return [parsed.hostname]
    except Exception:
        pass
    return []

@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(*, session: Session = Depends(get_session), project_in: ProjectCreate):
    try:
        urlparse(project_in.base_url)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base_url format")
        
    project = Project.model_validate(project_in)
    session.add(project)
    session.commit()
    session.refresh(project)
    
    # Automatically create default TargetConfig for the new project
    target_config = TargetConfig(
        project_id=project.id,
        allowed_hosts=get_default_allowed_hosts(project.base_url)
    )
    session.add(target_config)
    session.commit()
    
    return project

@router.get("", response_model=List[ProjectRead])
def read_projects(*, session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    projects = session.exec(select(Project).offset(skip).limit(limit)).all()
    return projects

@router.get("/{project_id}", response_model=ProjectRead)
def read_project(*, session: Session = Depends(get_session), project_id: uuid.UUID):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(*, session: Session = Depends(get_session), project_id: uuid.UUID, project_in: ProjectUpdate):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    update_data = project_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
        
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

from sqlmodel import delete
from app.models.scan_models import TestExecution, TestCase, ScanEvent, ScanJob
from app.models.openapi import Endpoint, UploadedSpec
from app.models.finding_models import Finding, Evidence
from app.models.auth_models import AuthConfig, Account, Role

@router.delete("/{project_id}")
def delete_project(*, session: Session = Depends(get_session), project_id: uuid.UUID):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Delete related records explicitly to prevent IntegrityError 
        # (if database level cascades are missing)
        
        # Findings & Evidence
        finding_subquery = select(Finding.id).where(Finding.project_id == project_id)
        session.exec(delete(Evidence).where(Evidence.finding_id.in_(finding_subquery)))
        session.exec(delete(Finding).where(Finding.project_id == project_id))

        # Scans and executions
        subquery = select(ScanJob.id).where(ScanJob.project_id == project_id)
        session.exec(delete(TestExecution).where(TestExecution.scan_id.in_(subquery)))
        session.exec(delete(ScanEvent).where(ScanEvent.scan_id.in_(subquery)))
        session.exec(delete(TestCase).where(TestCase.project_id == project_id))
        session.exec(delete(ScanJob).where(ScanJob.project_id == project_id))
        
        # OpenAPI
        session.exec(delete(Endpoint).where(Endpoint.project_id == project_id))
        session.exec(delete(UploadedSpec).where(UploadedSpec.project_id == project_id))
        
        # Auth Config
        session.exec(delete(AuthConfig).where(AuthConfig.project_id == project_id))
        session.exec(delete(Account).where(Account.project_id == project_id))
        session.exec(delete(Role).where(Role.project_id == project_id))
        
        session.delete(project)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"ok": True}

@router.get("/{project_id}/target-config", response_model=TargetConfigRead)
def read_target_config(*, session: Session = Depends(get_session), project_id: uuid.UUID):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.target_config:
        raise HTTPException(status_code=404, detail="Target config not found")
    return project.target_config

@router.patch("/{project_id}/target-config", response_model=TargetConfigRead)
def update_target_config(*, session: Session = Depends(get_session), project_id: uuid.UUID, config_in: TargetConfigUpdate):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    target_config = project.target_config
    if not target_config:
        raise HTTPException(status_code=404, detail="Target config not found")
        
    update_data = config_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(target_config, key, value)
        
    session.add(target_config)
    session.commit()
    session.refresh(target_config)
    return target_config

@router.post("/{project_id}/demo/minisub-setup")
def setup_minisub_demo(*, session: Session = Depends(get_session), project_id: uuid.UUID):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # 1. Update Project Base URL
    project.base_url = "http://vulnerable-saas:9000"
    session.add(project)
    
    # 1.5 Update Target Config allowed hosts
    target_config = project.target_config
    if target_config:
        if "vulnerable-saas" not in target_config.allowed_hosts:
            target_config.allowed_hosts = target_config.allowed_hosts + ["vulnerable-saas"]
        session.add(target_config)
    
    # 2. Setup Auth Config
    auth_config = session.exec(select(AuthConfig).where(AuthConfig.project_id == project_id)).first()
    if not auth_config:
        auth_config = AuthConfig(project_id=project_id)
    
    auth_config.auth_type = "jwt"
    auth_config.login_endpoint = "/auth/login"
    auth_config.method = "POST"
    auth_config.username_field = "email"
    auth_config.password_field = "password"
    auth_config.token_json_path = "access_token"
    auth_config.header_template = "Bearer {token}"
    session.add(auth_config)
    
    # Clear existing roles and accounts
    session.exec(delete(Account).where(Account.project_id == project_id))
    session.exec(delete(Role).where(Role.project_id == project_id))
    session.commit()
    
    # 3. Create Roles
    role_admin = Role(project_id=project_id, name="Admin", level=100)
    role_support = Role(project_id=project_id, name="Support", level=50)
    role_customer = Role(project_id=project_id, name="Customer", level=10)
    
    session.add_all([role_admin, role_support, role_customer])
    session.commit()
    
    # 4. Create Accounts
    from app.models.auth_models import encode_secret
    accounts = [
        Account(project_id=project_id, label="Admin User", username="admin@example.com", encrypted_secret=encode_secret("Password123"), role_id=role_admin.id, auth_type="password"),
        Account(project_id=project_id, label="Support Agent", username="support@example.com", encrypted_secret=encode_secret("Password123"), role_id=role_support.id, auth_type="password"),
        Account(project_id=project_id, label="Alice (Customer A)", username="customer_a@example.com", encrypted_secret=encode_secret("Password123"), role_id=role_customer.id, auth_type="password"),
        Account(project_id=project_id, label="Bob (Customer B)", username="customer_b@example.com", encrypted_secret=encode_secret("Password123"), role_id=role_customer.id, auth_type="password"),
    ]
    session.add_all(accounts)
    session.commit()
    
    # 5. Import OpenAPI Spec
    try:
        from app.api.routes_openapi import import_from_url, ImportUrlRequest
        import_from_url(
            session=session,
            project_id=project_id,
            body=ImportUrlRequest(url="http://vulnerable-saas:9000/openapi.json")
        )
    except Exception as e:
        print(f"Failed to import MiniSub OpenAPI spec: {e}")
        
    return {"ok": True, "message": "MiniSub Demo configured"}
import httpx
import time
import re

@router.post("/{project_id}/demo/crapi-setup")
def setup_crapi_demo(*, session: Session = Depends(get_session), project_id: uuid.UUID):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # 1. Update Project Base URL
    project.base_url = "http://host.docker.internal:8888"
    session.add(project)
    
    # 1.5 Update Target Config allowed hosts
    target_config = project.target_config
    if target_config:
        allowed = set(target_config.allowed_hosts)
        allowed.update(["crapi-web", "localhost", "host.docker.internal"])
        target_config.allowed_hosts = list(allowed)
        target_config.allow_destructive_tests = False
        target_config.allow_payment_tests = False
        session.add(target_config)
    
    # 2. Setup Auth Config
    auth_config = session.exec(select(AuthConfig).where(AuthConfig.project_id == project_id)).first()
    if not auth_config:
        auth_config = AuthConfig(project_id=project_id)
    
    auth_config.auth_type = "jwt"
    auth_config.login_endpoint = "/identity/api/auth/login"
    auth_config.method = "POST"
    auth_config.username_field = "email"
    auth_config.password_field = "password"
    auth_config.token_json_path = "token"
    auth_config.header_template = "Bearer {token}"
    session.add(auth_config)
    
    # Clear existing roles and accounts
    session.exec(delete(Account).where(Account.project_id == project_id))
    session.exec(delete(Role).where(Role.project_id == project_id))
    session.commit()
    
    # 3. Create Roles
    role_customer = Role(project_id=project_id, name="Customer", level=10)
    session.add(role_customer)
    session.commit()
    
    # 4. Seed users in crAPI via API
    users = [
        {"name": "Attacker", "email": "attacker@example.com", "number": "9999999999", "password": "Password123!"},
        {"name": "Victim", "email": "victim@example.com", "number": "8888888888", "password": "Password123!"},
        {"name": "Admin", "email": "admin@example.com", "number": "1111111111", "password": "Password123!"}
    ]
    
    # NOTE: Since this runs in the backend container, the crAPI instance is at host.docker.internal:8888 
    # and mailhog is at host.docker.internal:8025.
    CRAPI_URL = "http://host.docker.internal:8888"
    MAILHOG_URL = "http://host.docker.internal:8025/api/v2/messages"
    
    for u in users:
        resp = httpx.post(f"{CRAPI_URL}/identity/api/auth/signup", json=u)
        if resp.status_code != 200:
            continue
            
        otp = None
        for _ in range(10):
            try:
                mail_resp = httpx.get(MAILHOG_URL)
                if mail_resp.status_code == 200:
                    msgs = mail_resp.json().get("items", [])
                    for msg in msgs:
                        to_list = msg.get("Raw", {}).get("To", [])
                        if any(u['email'] in t for t in to_list):
                            body = msg.get("Raw", {}).get("Data", "")
                            match = re.search(r'OTP is\s*:\s*(\d{4})', body)
                            if match:
                                otp = match.group(1)
                                break
                    if otp: break
            except Exception:
                pass
            time.sleep(1)
            
        if otp:
            httpx.post(f"{CRAPI_URL}/identity/api/auth/v3/check-otp", json={"email": u['email'], "otp": otp})
    
    # 5. Create Accounts in FlowShield
    from app.models.auth_models import encode_secret
    accounts = []
    for u in users:
        accounts.append(
            Account(
                project_id=project_id, 
                label=u["name"], 
                username=u["email"], 
                encrypted_secret=encode_secret(u["password"]), 
                role_id=role_customer.id, 
                auth_type="password"
            )
        )
    session.add_all(accounts)
    session.commit()
    
    # 6. Import OpenAPI Spec
    try:
        import os
        from app.models.openapi import UploadedSpec
        from app.services.openapi_parser import parse_openapi_spec
        from app.api.routes_openapi import _clear_existing, _store_parsed

        spec_path = os.path.join(os.path.dirname(__file__), "crapi-openapi-spec.json")
        with open(spec_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        spec_record = UploadedSpec(
            project_id=project_id,
            source_type="file",
            original_filename="crapi-openapi-spec.json",
        )
        spec_dict, endpoints = parse_openapi_spec(raw_content)
        spec_record.raw_spec_json = spec_dict
        spec_record.parsed_successfully = True

        _clear_existing(session, project_id)
        _store_parsed(session, project_id, spec_record, endpoints)
    except Exception as e:
        print(f"Failed to import crAPI OpenAPI spec: {e}")
    
    return {"ok": True, "message": "crAPI Demo configured and seeded"}

@router.get("/{project_id}/readiness")
def check_project_readiness(*, session: Session = Depends(get_session), project_id: uuid.UUID):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    checks = []

    # Check 1: Target URL
    has_target = bool(project.base_url)
    checks.append({
        "name": "Target URL Configured",
        "status": "pass" if has_target else "fail",
        "message": "Base URL of the target API"
    })

    # Check 2: API Inventory
    endpoints_count = session.exec(select(Endpoint).where(Endpoint.project_id == project_id)).all()
    has_endpoints = len(endpoints_count) > 0
    checks.append({
        "name": "API Inventory",
        "status": "pass" if has_endpoints else "fail",
        "message": f"{len(endpoints_count)} endpoints discovered" if has_endpoints else "No OpenAPI spec uploaded"
    })

    # Check 3: Authentication
    auth_config = session.exec(select(AuthConfig).where(AuthConfig.project_id == project_id)).first()
    has_auth = auth_config is not None
    checks.append({
        "name": "Authentication Strategy",
        "status": "pass" if has_auth else "fail",
        "message": f"{auth_config.auth_type.upper()} configured" if has_auth else "No auth strategy defined"
    })

    # Check 4: Test Accounts
    accounts_count = session.exec(select(Account).where(Account.project_id == project_id)).all()
    has_accounts = len(accounts_count) > 0
    checks.append({
        "name": "Test Accounts",
        "status": "pass" if has_accounts else "fail",
        "message": f"{len(accounts_count)} accounts configured" if has_accounts else "No test accounts exist"
    })

    is_ready = has_target and has_endpoints and has_auth and has_accounts

    return {
        "ready": is_ready,
        "checks": checks
    }
