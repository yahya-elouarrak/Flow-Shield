from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.models import UserProfile

router = APIRouter(tags=["users"])


@router.api_route("/me", methods=["GET", "POST"], response_model=UserProfile, summary="Get current user profile")
def get_me(user: dict = Depends(get_current_user), request: dict = None):
    """
    Returns the authenticated user's profile.
    VULNERABLE: Accepts POST method which might bypass some assumed GET-only WAF rules.
    """
    return UserProfile(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        subscription_status=user.get("subscription_status"),
        plan=user.get("plan"),
    )
