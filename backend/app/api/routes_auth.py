"""
API routes for role, account, auth config, and login test management.
Secrets and raw tokens are NEVER returned in responses.
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.project import Project
from app.models.auth_models import (
    Role, RoleCreate, RoleRead, RoleUpdate,
    Account, AccountCreate, AccountRead, AccountUpdate,
    AuthConfig, AuthConfigRead, AuthConfigUpdate,
    AuthSession, AuthSessionRead, LoginTestResult,
    encode_secret,
)
from app.services.auth_manager import login_account

router = APIRouter(prefix="/projects/{project_id}", tags=["accounts & roles"])


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_project(session: Session, project_id: uuid.UUID) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _account_to_read(account: Account) -> AccountRead:
    """Convert an Account ORM object to its read schema, enriching with role/session info."""
    role_name = account.role.name if account.role else None
    login_status = None
    last_login_at = None
    if account.auth_session:
        if account.auth_session.last_error:
            login_status = "error"
        elif account.auth_session.masked_token:
            login_status = "success"
        last_login_at = account.auth_session.last_login_at

    return AccountRead(
        id=account.id,
        project_id=account.project_id,
        role_id=account.role_id,
        label=account.label,
        username=account.username,
        auth_type=account.auth_type,
        notes=account.notes,
        created_at=account.created_at,
        has_secret=bool(account.encrypted_secret),
        role_name=role_name,
        login_status=login_status,
        last_login_at=last_login_at,
    )


# ─── Roles CRUD ──────────────────────────────────────────────────────────────

@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED,
             summary="Create a role")
def create_role(
    *, session: Session = Depends(get_session),
    project_id: uuid.UUID, body: RoleCreate,
):
    _get_project(session, project_id)
    role = Role(project_id=project_id, **body.model_dump())
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@router.get("/roles", response_model=List[RoleRead], summary="List roles")
def list_roles(
    *, session: Session = Depends(get_session), project_id: uuid.UUID,
):
    _get_project(session, project_id)
    stmt = select(Role).where(Role.project_id == project_id).order_by(Role.level)
    return session.exec(stmt).all()


@router.patch("/roles/{role_id}", response_model=RoleRead, summary="Update a role")
def update_role(
    *, session: Session = Depends(get_session),
    project_id: uuid.UUID, role_id: uuid.UUID, body: RoleUpdate,
):
    _get_project(session, project_id)
    role = session.get(Role, role_id)
    if not role or role.project_id != project_id:
        raise HTTPException(status_code=404, detail="Role not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(role, key, value)
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@router.delete("/roles/{role_id}", summary="Delete a role")
def delete_role(
    *, session: Session = Depends(get_session),
    project_id: uuid.UUID, role_id: uuid.UUID,
):
    _get_project(session, project_id)
    role = session.get(Role, role_id)
    if not role or role.project_id != project_id:
        raise HTTPException(status_code=404, detail="Role not found")
    session.delete(role)
    session.commit()
    return {"ok": True}


# ─── Accounts CRUD ───────────────────────────────────────────────────────────

@router.post("/accounts", response_model=AccountRead, status_code=status.HTTP_201_CREATED,
             summary="Create a test account")
def create_account(
    *, session: Session = Depends(get_session),
    project_id: uuid.UUID, body: AccountCreate,
):
    _get_project(session, project_id)

    # Validate role_id if provided
    if body.role_id:
        role = session.get(Role, body.role_id)
        if not role or role.project_id != project_id:
            raise HTTPException(status_code=400, detail="Invalid role_id")

    account = Account(
        project_id=project_id,
        label=body.label,
        username=body.username,
        role_id=body.role_id,
        auth_type=body.auth_type,
        notes=body.notes,
        encrypted_secret=encode_secret(body.secret) if body.secret else None,
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return _account_to_read(account)


@router.get("/accounts", response_model=List[AccountRead],
            summary="List test accounts (secrets never returned)")
def list_accounts(
    *, session: Session = Depends(get_session), project_id: uuid.UUID,
):
    _get_project(session, project_id)
    stmt = select(Account).where(Account.project_id == project_id)
    accounts = session.exec(stmt).all()
    return [_account_to_read(a) for a in accounts]


@router.patch("/accounts/{account_id}", response_model=AccountRead,
              summary="Update a test account")
def update_account(
    *, session: Session = Depends(get_session),
    project_id: uuid.UUID, account_id: uuid.UUID, body: AccountUpdate,
):
    _get_project(session, project_id)
    account = session.get(Account, account_id)
    if not account or account.project_id != project_id:
        raise HTTPException(status_code=404, detail="Account not found")

    update_data = body.model_dump(exclude_unset=True)

    # Handle secret separately
    new_secret = update_data.pop("secret", None)
    if new_secret is not None:
        account.encrypted_secret = encode_secret(new_secret)

    # Validate role_id if being updated
    if "role_id" in update_data and update_data["role_id"]:
        role = session.get(Role, update_data["role_id"])
        if not role or role.project_id != project_id:
            raise HTTPException(status_code=400, detail="Invalid role_id")

    for key, value in update_data.items():
        setattr(account, key, value)

    session.add(account)
    session.commit()
    session.refresh(account)
    return _account_to_read(account)


@router.delete("/accounts/{account_id}", summary="Delete a test account")
def delete_account(
    *, session: Session = Depends(get_session),
    project_id: uuid.UUID, account_id: uuid.UUID,
):
    _get_project(session, project_id)
    account = session.get(Account, account_id)
    if not account or account.project_id != project_id:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(account)
    session.commit()
    return {"ok": True}


# ─── AuthConfig ──────────────────────────────────────────────────────────────

@router.get("/auth-config", response_model=Optional[AuthConfigRead],
            summary="Get auth configuration")
def get_auth_config(
    *, session: Session = Depends(get_session), project_id: uuid.UUID,
):
    _get_project(session, project_id)
    stmt = select(AuthConfig).where(AuthConfig.project_id == project_id)
    config = session.exec(stmt).first()
    return config


@router.patch("/auth-config", response_model=AuthConfigRead,
              summary="Create or update auth configuration")
def upsert_auth_config(
    *, session: Session = Depends(get_session),
    project_id: uuid.UUID, body: AuthConfigUpdate,
):
    _get_project(session, project_id)
    stmt = select(AuthConfig).where(AuthConfig.project_id == project_id)
    config = session.exec(stmt).first()

    if config:
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(config, key, value)
    else:
        config = AuthConfig(project_id=project_id, **body.model_dump(exclude_unset=True))

    session.add(config)
    session.commit()
    session.refresh(config)
    return config


# ─── Login Tests ─────────────────────────────────────────────────────────────

@router.post("/accounts/{account_id}/login-test", response_model=LoginTestResult,
             summary="Test login for a single account")
def test_account_login(
    *, session: Session = Depends(get_session),
    project_id: uuid.UUID, account_id: uuid.UUID,
):
    """
    Attempt to login a single account against the target API.
    Returns masked token on success, error message on failure.
    """
    project = _get_project(session, project_id)
    account = session.get(Account, account_id)
    if not account or account.project_id != project_id:
        raise HTTPException(status_code=404, detail="Account not found")

    stmt = select(AuthConfig).where(AuthConfig.project_id == project_id)
    auth_config = session.exec(stmt).first()
    if not auth_config:
        raise HTTPException(status_code=400, detail="Auth configuration not set up")

    success, masked, error = login_account(session, project, auth_config, account)
    session.commit()

    return LoginTestResult(
        account_id=account.id,
        account_label=account.label,
        success=success,
        masked_token=masked,
        error=error,
    )


@router.post("/auth/test", response_model=List[LoginTestResult],
             summary="Test login for all accounts")
def test_all_logins(
    *, session: Session = Depends(get_session), project_id: uuid.UUID,
):
    """
    Attempt to login all accounts for a project.
    Returns per-account results with masked tokens.
    """
    project = _get_project(session, project_id)

    stmt = select(AuthConfig).where(AuthConfig.project_id == project_id)
    auth_config = session.exec(stmt).first()
    if not auth_config:
        raise HTTPException(status_code=400, detail="Auth configuration not set up")

    stmt = select(Account).where(Account.project_id == project_id)
    accounts = session.exec(stmt).all()
    if not accounts:
        raise HTTPException(status_code=400, detail="No accounts to test")

    results = []
    for account in accounts:
        success, masked, error = login_account(session, project, auth_config, account)
        results.append(LoginTestResult(
            account_id=account.id,
            account_label=account.label,
            success=success,
            masked_token=masked,
            error=error,
        ))

    session.commit()
    return results
