from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app import database
from app.config import settings
from app.auth import get_current_user, require_role
from app.models import UserProfile, AdminUserUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserProfile],
            summary="List all users (admin only)")
def list_all_users(user: dict = Depends(get_current_user)):
    """
    List all registered users.

    VULNERABLE (BFLA): Any authenticated user can access.
    SECURE: Admin role required.
    """
    if not settings.VULNERABLE_MODE:
        if user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")

    return [
        UserProfile(
            id=u["id"],
            email=u["email"],
            name=u["name"],
            role=u["role"],
            subscription_status=u.get("subscription_status"),
            plan=u.get("plan"),
        )
        for u in database.users.values()
    ]


@router.patch("/users/{user_id}", response_model=UserProfile,
              summary="Update a user (admin only)")
def update_user(user_id: str, body: AdminUserUpdate, user: dict = Depends(get_current_user)):
    """
    Update user fields.

    VULNERABLE (Mass Assignment): Accepts role and subscription_status fields
    from any user, allowing privilege escalation.

    SECURE: Admin-only, rejects privileged fields from non-admin.
    """
    target = database.users.get(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = body.model_dump(exclude_unset=True)

    if settings.VULNERABLE_MODE:
        # ── VULN: Mass assignment — accepts role, subscription_status ─────
        for key, value in update_data.items():
            if key != "hashed_password":
                target[key] = value
    else:
        # ── SECURE: Admin-only, block privileged fields ──────────────────
        if user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")

        privileged_fields = {"role", "subscription_status"}
        for key, value in update_data.items():
            if key in privileged_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot update privileged field: {key}",
                )
            target[key] = value

    return UserProfile(
        id=target["id"],
        email=target["email"],
        name=target["name"],
        role=target["role"],
        subscription_status=target.get("subscription_status"),
        plan=target.get("plan"),
    )
