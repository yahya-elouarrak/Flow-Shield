import uuid
from fastapi import APIRouter, Depends, HTTPException

from app import database
from app.config import settings
from app.auth import get_current_user
from app.models import CheckoutRequest, PaymentResponse, ConfirmPaymentRequest

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/checkout", response_model=PaymentResponse,
             summary="Initiate a payment for a subscription")
def checkout(body: CheckoutRequest, user: dict = Depends(get_current_user)):
    """
    Create a payment for a subscription.

    VULNERABLE: Accepts client-supplied amount (price manipulation) and negative amounts.
    SECURE: Calculates price from plan, rejects negatives.
    """
    sub = database.subscriptions.get(body.subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if sub["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not your subscription")

    plan = database.plans.get(sub["plan_id"])
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if settings.VULNERABLE_MODE:
        # ── VULN: Price manipulation + negative amount ───────────────────
        amount = body.amount if body.amount is not None else plan["price"]
    else:
        # ── SECURE: Server-side price calculation ────────────────────────
        amount = plan["price"]
        if body.amount is not None and body.amount != plan["price"]:
            raise HTTPException(
                status_code=400,
                detail=f"Amount must match plan price: {plan['price']}",
            )
        if amount < 0:
            raise HTTPException(status_code=400, detail="Amount cannot be negative")

    pay_id = f"pay-{uuid.uuid4().hex[:8]}"
    payment = {
        "id": pay_id,
        "subscription_id": sub["id"],
        "user_id": user["id"],
        "amount": amount,
        "status": "pending",
        "invoice_id": None,
    }
    database.payments[pay_id] = payment

    return PaymentResponse(**payment)


@router.post("/confirm", response_model=PaymentResponse,
             summary="Confirm a pending payment")
def confirm_payment(body: ConfirmPaymentRequest, user: dict = Depends(get_current_user)):
    """Confirm a pending payment and generate an invoice."""
    payment = database.payments.get(body.payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not your payment")

    if payment["status"] == "confirmed":
        return PaymentResponse(**payment)

    # Confirm payment
    payment["status"] = "confirmed"

    # Mark subscription as payment confirmed
    sub = database.subscriptions.get(payment["subscription_id"])
    if sub:
        sub["payment_confirmed"] = True

    # Generate invoice
    inv_id = f"inv-{uuid.uuid4().hex[:8]}"
    invoice = {
        "id": inv_id,
        "user_id": user["id"],
        "subscription_id": payment["subscription_id"],
        "amount": payment["amount"],
        "status": "paid",
        "created_at": "2026-07-22T10:00:00Z",
        "internal_user_id": f"internal-ref-{uuid.uuid4().hex[:6]}",
        "payment_processor_ref": f"stripe_pi_{uuid.uuid4().hex[:12]}",
        "cost_basis": round(payment["amount"] * 0.25, 2),
        "debug_notes": "Auto-generated on payment confirmation.",
    }
    database.invoices[inv_id] = invoice
    payment["invoice_id"] = inv_id

    return PaymentResponse(**payment)
