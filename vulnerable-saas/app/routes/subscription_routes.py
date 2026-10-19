import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app import database
from app.config import settings
from app.auth import get_current_user
from app.models import Plan, SelectPlanRequest, SubscriptionResponse

router = APIRouter(tags=["subscriptions"])


@router.get("/plans", response_model=List[Plan], summary="List available subscription plans")
def list_plans():
    """Returns all available subscription plans. Public endpoint."""
    return [Plan(**p) for p in database.plans.values()]


@router.post("/subscriptions/select-plan", response_model=SubscriptionResponse,
             summary="Select a subscription plan")
def select_plan(body: SelectPlanRequest, user: dict = Depends(get_current_user)):
    """Choose a subscription plan. Creates a pending subscription."""
    plan = database.plans.get(body.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    sub_id = f"sub-{uuid.uuid4().hex[:8]}"
    sub = {
        "id": sub_id,
        "user_id": user["id"],
        "plan_id": plan["id"],
        "plan_name": plan["name"],
        "status": "pending",
        "payment_confirmed": False,
    }
    database.subscriptions[sub_id] = sub

    # Update user record
    user["plan"] = plan["id"]
    user["subscription_status"] = "pending"

    return SubscriptionResponse(**sub)


@router.get("/subscriptions/me", response_model=List[SubscriptionResponse],
            summary="Get current user's subscriptions")
def my_subscriptions(user: dict = Depends(get_current_user)):
    """Returns all subscriptions for the authenticated user."""
    result = []
    for sub in database.subscriptions.values():
        if sub["user_id"] == user["id"]:
            result.append(SubscriptionResponse(**sub))
    return result


@router.post("/subscriptions/activate", response_model=SubscriptionResponse,
             summary="Activate a subscription")
def activate_subscription(body: SelectPlanRequest, user: dict = Depends(get_current_user)):
    """
    Activate a pending subscription.

    VULNERABLE: Allows activation without confirmed payment.
    SECURE: Requires payment_confirmed=True.
    """
    # Find the user's subscription for this plan
    target_sub = None
    for sub in database.subscriptions.values():
        if sub["user_id"] == user["id"] and sub["plan_id"] == body.plan_id:
            target_sub = sub
            break

    if not target_sub:
        raise HTTPException(status_code=404, detail="No subscription found for this plan")

    if target_sub["status"] == "active":
        return SubscriptionResponse(**target_sub)

    # ── VULNERABILITY: Payment bypass ────────────────────────────────────
    if not settings.VULNERABLE_MODE:
        if not target_sub["payment_confirmed"]:
            raise HTTPException(
                status_code=400,
                detail="Cannot activate: payment not confirmed",
            )

    target_sub["status"] = "active"
    user["subscription_status"] = "active"

    return SubscriptionResponse(**target_sub)
