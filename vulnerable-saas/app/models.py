"""
Pydantic models for request/response schemas.
Used by FastAPI to generate clean OpenAPI documentation.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: str = Field(..., example="newuser@example.com")
    password: str = Field(..., min_length=6, example="MyPassword123")
    name: str = Field(..., example="New User")


class UserLogin(BaseModel):
    email: str = Field(..., example="customer_a@example.com")
    password: str = Field(..., example="Password123")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── Users ───────────────────────────────────────────────────────────────────

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    role: str
    subscription_status: Optional[str] = None
    plan: Optional[str] = None


class UserProfileInternal(UserProfile):
    """Extended profile with internal fields (for admin)."""
    hashed_password: Optional[str] = None


class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    subscription_status: Optional[str] = None


# ─── Plans ───────────────────────────────────────────────────────────────────

class Plan(BaseModel):
    id: str
    name: str
    price: float
    features: List[str]


# ─── Subscriptions ───────────────────────────────────────────────────────────

class SelectPlanRequest(BaseModel):
    plan_id: str = Field(..., example="plan-basic")


class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    plan_name: str
    status: str  # pending, active, cancelled
    payment_confirmed: bool


# ─── Payments ────────────────────────────────────────────────────────────────

class CheckoutRequest(BaseModel):
    subscription_id: str = Field(..., example="sub-001")
    amount: Optional[float] = Field(default=None, example=9.99)


class PaymentResponse(BaseModel):
    id: str
    subscription_id: str
    amount: float
    status: str  # pending, confirmed
    invoice_id: Optional[str] = None


class ConfirmPaymentRequest(BaseModel):
    payment_id: str = Field(..., example="pay-001")


# ─── Invoices ────────────────────────────────────────────────────────────────

class InvoiceResponse(BaseModel):
    id: str
    user_id: str
    subscription_id: str
    amount: float
    status: str
    created_at: str


class InvoiceDetailVulnerable(InvoiceResponse):
    """Leaks internal fields in vulnerable mode."""
    internal_user_id: Optional[str] = None
    payment_processor_ref: Optional[str] = None
    cost_basis: Optional[float] = None
    debug_notes: Optional[str] = None


# ─── Coupons ─────────────────────────────────────────────────────────────────

class ApplyCouponRequest(BaseModel):
    code: str = Field(..., example="SAVE20")
    subscription_id: str = Field(..., example="sub-001")


class CouponResponse(BaseModel):
    id: str
    code: str
    discount_percent: int
    applied: bool
    message: str


# ─── Refunds ─────────────────────────────────────────────────────────────────

class RefundRequest(BaseModel):
    invoice_id: str = Field(..., example="inv-001")
    amount: float = Field(..., example=9.99)
    reason: str = Field(..., example="Not satisfied with the service")


class RefundResponse(BaseModel):
    id: str
    invoice_id: str
    user_id: str
    amount: float
    reason: str
    status: str  # pending, approved, rejected


# ─── Premium ─────────────────────────────────────────────────────────────────

class PremiumFeature(BaseModel):
    id: str
    name: str
    description: str
    tier: str
