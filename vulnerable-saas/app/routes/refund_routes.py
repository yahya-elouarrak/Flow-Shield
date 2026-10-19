import uuid
from fastapi import APIRouter, Depends, HTTPException

from app import database
from app.config import settings
from app.auth import get_current_user, require_role
from app.models import RefundRequest, RefundResponse

router = APIRouter(tags=["refunds"])


@router.post("/refunds/request", response_model=RefundResponse,
             summary="Request a refund for an invoice")
def request_refund(body: RefundRequest, user: dict = Depends(get_current_user)):
    """
    Submit a refund request.

    VULNERABLE: Allows negative refund amount.
    SECURE: Validates positive amount.
    """
    invoice = database.invoices.get(body.invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not your invoice")

    # ── VULNERABILITY: Negative amount ───────────────────────────────────
    if not settings.VULNERABLE_MODE:
        if body.amount <= 0:
            raise HTTPException(status_code=400, detail="Refund amount must be positive")
        if body.amount > invoice["amount"]:
            raise HTTPException(status_code=400, detail="Refund amount exceeds invoice total")

    ref_id = f"ref-{uuid.uuid4().hex[:8]}"
    refund = {
        "id": ref_id,
        "invoice_id": body.invoice_id,
        "user_id": user["id"],
        "amount": body.amount,
        "reason": body.reason,
        "status": "pending",
    }
    database.refunds[ref_id] = refund

    return RefundResponse(**refund)


@router.post("/support/refunds/{refund_id}/approve", response_model=RefundResponse,
             summary="Approve a pending refund (support/admin only)")
def approve_refund(refund_id: str, user: dict = Depends(get_current_user)):
    """
    Approve a pending refund request.

    VULNERABLE (BFLA): Any authenticated user can approve (no role check).
    SECURE: Only support or admin roles can approve.
    """
    refund = database.refunds.get(refund_id)
    if not refund:
        raise HTTPException(status_code=404, detail="Refund not found")

    # ── VULNERABILITY: BFLA — no role check ──────────────────────────────
    if not settings.VULNERABLE_MODE:
        if user["role"] not in ("support", "admin"):
            raise HTTPException(status_code=403, detail="Requires support or admin role")

    if refund["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Refund already {refund['status']}")

    refund["status"] = "approved"
    return RefundResponse(**refund)
