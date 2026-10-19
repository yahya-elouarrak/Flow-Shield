from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app import database
from app.config import settings
from app.auth import get_current_user
from app.models import InvoiceResponse, InvoiceDetailVulnerable

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/me", response_model=List[InvoiceResponse],
            summary="List current user's invoices")
def my_invoices(user: dict = Depends(get_current_user)):
    """Returns all invoices belonging to the authenticated user."""
    result = []
    for inv in database.invoices.values():
        if inv["user_id"] == user["id"]:
            result.append(InvoiceResponse(
                id=inv["id"],
                user_id=inv["user_id"],
                subscription_id=inv["subscription_id"],
                amount=inv["amount"],
                status=inv["status"],
                created_at=inv["created_at"],
            ))
    return result


@router.get("/{invoice_id}",
            summary="Get invoice by ID")
def get_invoice(invoice_id: str, user: dict = Depends(get_current_user)):
    """
    Retrieve a specific invoice by its ID.

    VULNERABLE (BOLA/IDOR): No ownership check — any user can read any invoice.
    Also leaks internal fields (excessive data exposure).

    SECURE: Enforces ownership, strips internal fields.
    """
    invoice = database.invoices.get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if settings.VULNERABLE_MODE:
        # ── VULN: No ownership check + excessive data exposure ───────────
        return InvoiceDetailVulnerable(
            id=invoice["id"],
            user_id=invoice["user_id"],
            subscription_id=invoice["subscription_id"],
            amount=invoice["amount"],
            status=invoice["status"],
            created_at=invoice["created_at"],
            internal_user_id=invoice.get("internal_user_id"),
            payment_processor_ref=invoice.get("payment_processor_ref"),
            cost_basis=invoice.get("cost_basis"),
            debug_notes=invoice.get("debug_notes"),
        )
    else:
        # ── SECURE: Ownership check + no internal fields ─────────────────
        if invoice["user_id"] != user["id"] and user["role"] not in ("admin", "support"):
            raise HTTPException(status_code=403, detail="Access denied: not your invoice")

        return InvoiceResponse(
            id=invoice["id"],
            user_id=invoice["user_id"],
            subscription_id=invoice["subscription_id"],
            amount=invoice["amount"],
            status=invoice["status"],
            created_at=invoice["created_at"],
        )
