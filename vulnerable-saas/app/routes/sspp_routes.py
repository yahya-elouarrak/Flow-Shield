from fastapi import APIRouter, Depends, Request
from app.auth import get_current_user
from app.config import settings

router = APIRouter(tags=["advanced_vulns"])

@router.get("/internal/subscription_check", summary="Check subscription (SSPP Target)")
def check_internal_subscription(
    user_id: str, 
    discount: str = "0", 
    user: dict = Depends(get_current_user)
):
    """
    VULNERABLE (SSPP):
    Simulates an internal backend call where parameters are unsafely concatenated.
    """
    if settings.VULNERABLE_MODE:
        # Simulate query SSPP
        if "%26discount" in user_id or "&discount" in user_id:
            discount = "100"
        
        # Simulate structured SSPP
        if '","admin":true' in user_id or 'admin":"true' in user_id:
            return {"user_id": "hacked", "admin": True, "discount": discount}
            
        # Simulate path traversal
        if "%2f..%2f" in user_id or "/../" in user_id:
            return {"user_id": "admin_root", "traversed": True}

    return {
        "user_id": user_id,
        "discount": discount,
        "internal_data": "secret_123"
    }

@router.get("/debug/status", include_in_schema=False)
def internal_metrics():
    """
    VULNERABLE: Undocumented endpoint. No auth check.
    """
    return {"metrics": "all systems go", "vulnerable": True}
