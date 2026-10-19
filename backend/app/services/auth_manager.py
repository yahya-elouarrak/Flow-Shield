"""
Authentication Manager service.

Handles login automation against target APIs:
- Builds login URL from project base_url + auth_config.login_endpoint
- Sends login request with configured field names
- Extracts token using token_json_path
- Returns masked result (raw token never stored or returned via API)

IMPORTANT: Raw tokens are only held in-memory during scan execution.
They are NEVER sent to Ollama, logged, or returned in API responses.
"""

import httpx
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlmodel import Session

from app.models.auth_models import (
    Account, AuthConfig, AuthSession,
    decode_secret, mask_token,
)
from app.models.project import Project


def _extract_token(data: dict, json_path: str) -> Optional[str]:
    """
    Extract a value from a nested dict using dot-notation path.
    E.g., "access_token" → data["access_token"]
    E.g., "data.token" → data["data"]["token"]
    """
    parts = json_path.strip().split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return str(current) if current is not None else None


def login_account(
    session: Session,
    project: Project,
    auth_config: AuthConfig,
    account: Account,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Attempt to login an account against the target API.

    Returns: (success, masked_token_or_none, error_or_none)

    The raw token is intentionally discarded after masking.
    """
    # Decode the stored secret
    if not account.encrypted_secret:
        return False, None, "No secret/password stored for this account"

    try:
        secret = decode_secret(account.encrypted_secret)
    except Exception:
        return False, None, "Failed to decode stored secret"

    # Build login URL
    if not auth_config.login_endpoint:
        return False, None, "No login endpoint configured"

    base = project.base_url.rstrip("/")
    endpoint = auth_config.login_endpoint.lstrip("/")
    login_url = f"{base}/{endpoint}"

    # Build request body
    body = {
        auth_config.username_field: account.username,
        auth_config.password_field: secret,
    }

    # Send login request
    try:
        response = httpx.request(
            method=auth_config.method.upper(),
            url=login_url,
            json=body,
            timeout=10.0,
            follow_redirects=True,
        )
    except httpx.RequestError as e:
        error_msg = f"Connection failed: {str(e)}"
        _update_auth_session(session, account.id, None, error_msg)
        return False, None, error_msg

    if response.status_code >= 400:
        error_msg = f"Login failed: HTTP {response.status_code}"
        try:
            detail = response.json().get("detail", "")
            if detail:
                error_msg += f" — {detail}"
        except Exception:
            pass
        _update_auth_session(session, account.id, None, error_msg)
        return False, None, error_msg

    # Parse response
    try:
        resp_data = response.json()
    except Exception:
        error_msg = "Login response is not valid JSON"
        _update_auth_session(session, account.id, None, error_msg)
        return False, None, error_msg

    # Extract token
    raw_token = _extract_token(resp_data, auth_config.token_json_path)
    if not raw_token:
        error_msg = f"Token not found at path '{auth_config.token_json_path}' in response"
        _update_auth_session(session, account.id, None, error_msg)
        return False, None, error_msg

    # Mask the token — raw token is intentionally discarded after this
    masked = mask_token(raw_token)

    # Update auth session
    _update_auth_session(session, account.id, masked, None)

    return True, masked, None


def _update_auth_session(
    session: Session,
    account_id,
    masked_token: Optional[str],
    error: Optional[str],
) -> None:
    """Create or update the AuthSession for an account."""
    from sqlmodel import select

    stmt = select(AuthSession).where(AuthSession.account_id == account_id)
    auth_session = session.exec(stmt).first()

    now = datetime.now(timezone.utc)

    if auth_session:
        auth_session.masked_token = masked_token
        auth_session.last_error = error
        auth_session.last_login_at = now
    else:
        auth_session = AuthSession(
            account_id=account_id,
            masked_token=masked_token,
            last_login_at=now,
            last_error=error,
        )

    session.add(auth_session)
    session.flush()
