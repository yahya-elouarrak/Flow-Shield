"""
Models for FlowShield account, role, auth configuration, and auth session management.
Secrets are never returned in API read schemas.
"""

import uuid
import base64
from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSON

from .base import TimestampMixin


# ─── Secret helpers ──────────────────────────────────────────────────────────
# SECURITY TODO: Replace base64 with proper encryption (e.g., Fernet/AES)
# using a key from environment variable. Base64 is NOT encryption — it is
# only used here to avoid storing plaintext in the MVP database.

def encode_secret(plaintext: str) -> str:
    """Encode a secret for storage. NOT real encryption."""
    return base64.b64encode(plaintext.encode("utf-8")).decode("utf-8")


def decode_secret(encoded: str) -> str:
    """Decode a stored secret. NOT real decryption."""
    return base64.b64decode(encoded.encode("utf-8")).decode("utf-8")


def mask_token(token: str) -> str:
    """Mask a token for display: first 8 chars + ... + last 4 chars."""
    if len(token) <= 16:
        return token[:4] + "..." + token[-2:]
    return token[:8] + "..." + token[-4:]


# ─── Role ────────────────────────────────────────────────────────────────────

class RoleBase(SQLModel):
    name: str = Field(max_length=100)
    level: int = Field(default=1)
    description: Optional[str] = Field(default=None, max_length=500)


class Role(RoleBase, table=True):
    __tablename__ = "roles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    accounts: List["Account"] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: Optional[datetime]


class RoleUpdate(SQLModel):
    name: Optional[str] = None
    level: Optional[int] = None
    description: Optional[str] = None


# ─── Account ────────────────────────────────────────────────────────────────

class AccountBase(SQLModel):
    label: str = Field(max_length=100)
    username: str = Field(max_length=255)
    auth_type: str = Field(default="password", max_length=50)
    notes: Optional[str] = Field(default=None, max_length=1000)


class Account(AccountBase, table=True):
    __tablename__ = "accounts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", index=True)
    role_id: Optional[uuid.UUID] = Field(default=None, foreign_key="roles.id")
    encrypted_secret: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    role: Optional[Role] = Relationship(back_populates="accounts")
    auth_session: Optional["AuthSession"] = Relationship(
        back_populates="account",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )


class AccountCreate(AccountBase):
    role_id: Optional[uuid.UUID] = None
    secret: Optional[str] = None  # plaintext password/token, encoded before storage


class AccountRead(AccountBase):
    """Read schema — secret is NEVER included."""
    id: uuid.UUID
    project_id: uuid.UUID
    role_id: Optional[uuid.UUID]
    created_at: Optional[datetime]
    has_secret: bool = False  # indicates if a secret is stored
    role_name: Optional[str] = None
    login_status: Optional[str] = None  # from auth_session
    last_login_at: Optional[datetime] = None


class AccountUpdate(SQLModel):
    label: Optional[str] = None
    username: Optional[str] = None
    role_id: Optional[uuid.UUID] = None
    auth_type: Optional[str] = None
    notes: Optional[str] = None
    secret: Optional[str] = None  # if provided, updates the stored secret


# ─── AuthConfig ──────────────────────────────────────────────────────────────

class AuthConfigBase(SQLModel):
    auth_type: str = Field(default="jwt", max_length=50)  # jwt, api_key, cookie, none
    login_endpoint: Optional[str] = Field(default=None, max_length=500)
    method: str = Field(default="POST", max_length=10)
    username_field: str = Field(default="email", max_length=100)
    password_field: str = Field(default="password", max_length=100)
    token_json_path: str = Field(default="access_token", max_length=200)
    header_template: str = Field(default="Bearer {token}", max_length=500)
    refresh_endpoint: Optional[str] = Field(default=None, max_length=500)


class AuthConfig(AuthConfigBase, table=True):
    __tablename__ = "auth_configs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", unique=True, index=True)


class AuthConfigRead(AuthConfigBase):
    id: uuid.UUID
    project_id: uuid.UUID


class AuthConfigUpdate(SQLModel):
    auth_type: Optional[str] = None
    login_endpoint: Optional[str] = None
    method: Optional[str] = None
    username_field: Optional[str] = None
    password_field: Optional[str] = None
    token_json_path: Optional[str] = None
    header_template: Optional[str] = None
    refresh_endpoint: Optional[str] = None


# ─── AuthSession ─────────────────────────────────────────────────────────────

class AuthSession(SQLModel, table=True):
    __tablename__ = "auth_sessions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_id: uuid.UUID = Field(foreign_key="accounts.id", unique=True, index=True)
    masked_token: Optional[str] = Field(default=None, max_length=200)
    expires_at: Optional[datetime] = Field(default=None)
    last_login_at: Optional[datetime] = Field(default=None)
    last_error: Optional[str] = Field(default=None, sa_column=Column(Text))

    account: Optional[Account] = Relationship(back_populates="auth_session")


class AuthSessionRead(SQLModel):
    account_id: uuid.UUID
    masked_token: Optional[str]
    last_login_at: Optional[datetime]
    last_error: Optional[str]


class LoginTestResult(SQLModel):
    account_id: uuid.UUID
    account_label: str
    success: bool
    masked_token: Optional[str] = None
    error: Optional[str] = None
