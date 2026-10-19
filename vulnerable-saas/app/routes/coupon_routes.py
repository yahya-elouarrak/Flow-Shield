from fastapi import APIRouter, Depends, HTTPException

from app import database
from app.config import settings
from app.auth import get_current_user
from app.models import ApplyCouponRequest, CouponResponse

router = APIRouter(prefix="/coupons", tags=["coupons"])


@router.post("/apply", response_model=CouponResponse,
             summary="Apply a coupon code to a subscription")
def apply_coupon(body: ApplyCouponRequest, user: dict = Depends(get_current_user)):
    """
    Apply a coupon/discount code.

    VULNERABLE: Same coupon reusable unlimited times, no rate limiting.
    SECURE: Tracks per-user usage, blocks reuse.
    """
    # Find coupon by code
    coupon = None
    for c in database.coupons.values():
        if c["code"] == body.code:
            coupon = c
            break

    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")

    if not coupon["active"]:
        raise HTTPException(status_code=400, detail="Coupon is expired or inactive")

    # Check subscription exists
    sub = database.subscriptions.get(body.subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if sub["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not your subscription")

    usage_key = f"{user['id']}:{coupon['id']}"

    if settings.VULNERABLE_MODE:
        # ── VULN: No usage check, unlimited reuse ────────────────────────
        database.coupon_usage[usage_key] = database.coupon_usage.get(usage_key, 0) + 1
        return CouponResponse(
            id=coupon["id"],
            code=coupon["code"],
            discount_percent=coupon["discount_percent"],
            applied=True,
            message=f"{coupon['discount_percent']}% discount applied!",
        )
    else:
        # ── SECURE: Block reuse ──────────────────────────────────────────
        if database.coupon_usage.get(usage_key, 0) > 0:
            raise HTTPException(status_code=400, detail="Coupon already used")

        database.coupon_usage[usage_key] = 1
        return CouponResponse(
            id=coupon["id"],
            code=coupon["code"],
            discount_percent=coupon["discount_percent"],
            applied=True,
            message=f"{coupon['discount_percent']}% discount applied!",
        )
