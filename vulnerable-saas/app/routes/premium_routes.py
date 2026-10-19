from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app import database
from app.config import settings
from app.auth import get_current_user
from app.models import PremiumFeature

router = APIRouter(prefix="/premium", tags=["premium"])


@router.get("/features", response_model=List[PremiumFeature],
            summary="Access premium features")
def get_premium_features(user: dict = Depends(get_current_user)):
    """
    Access premium-only features.

    VULNERABLE: Returns features regardless of subscription status.
    SECURE: Requires active premium subscription.
    """
    if not settings.VULNERABLE_MODE:
        # ── SECURE: Check subscription ───────────────────────────────────
        if user.get("subscription_status") != "active":
            raise HTTPException(status_code=403, detail="Active subscription required")

        if user.get("plan") != "plan-premium":
            raise HTTPException(status_code=403, detail="Premium plan required")

    return [PremiumFeature(**f) for f in database.premium_features.values()]
