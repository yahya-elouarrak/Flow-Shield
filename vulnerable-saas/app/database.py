"""
In-memory database with deterministic seed data.
Resets cleanly on every container restart.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─── Tables (dict-based) ────────────────────────────────────────────────────

users: dict = {}
subscriptions: dict = {}
invoices: dict = {}
coupons: dict = {}
refunds: dict = {}
payments: dict = {}
plans: dict = {}
premium_features: dict = {}

# Track coupon usage per user (for secure mode)
coupon_usage: dict = {}  # { "user_id:coupon_id": count }


def seed():
    """Populate all tables with deterministic test data."""
    global users, subscriptions, invoices, coupons, refunds, payments, plans, premium_features, coupon_usage

    # ── Plans ────────────────────────────────────────────────────────────
    plans.clear()
    plans.update({
        "plan-free": {
            "id": "plan-free",
            "name": "Free",
            "price": 0.0,
            "features": ["Basic dashboard", "5 API calls/day"],
        },
        "plan-basic": {
            "id": "plan-basic",
            "name": "Basic",
            "price": 9.99,
            "features": ["Full dashboard", "1000 API calls/day", "Email support"],
        },
        "plan-premium": {
            "id": "plan-premium",
            "name": "Premium",
            "price": 29.99,
            "features": ["Full dashboard", "Unlimited API calls", "Priority support", "Advanced analytics", "Custom integrations"],
        },
    })

    # ── Users ────────────────────────────────────────────────────────────
    users.clear()
    hashed = pwd_context.hash("Password123")
    users.update({
        "user-001": {
            "id": "user-001",
            "email": "customer_a@example.com",
            "name": "Alice Customer",
            "role": "customer",
            "hashed_password": hashed,
            "subscription_status": "active",
            "plan": "plan-basic",
        },
        "user-002": {
            "id": "user-002",
            "email": "customer_b@example.com",
            "name": "Bob Customer",
            "role": "customer",
            "hashed_password": hashed,
            "subscription_status": "active",
            "plan": "plan-premium",
        },
        "user-003": {
            "id": "user-003",
            "email": "support@example.com",
            "name": "Support Agent",
            "role": "support",
            "hashed_password": hashed,
            "subscription_status": None,
            "plan": None,
        },
        "user-004": {
            "id": "user-004",
            "email": "admin@example.com",
            "name": "Admin User",
            "role": "admin",
            "hashed_password": hashed,
            "subscription_status": None,
            "plan": None,
        },
    })

    # ── Subscriptions ────────────────────────────────────────────────────
    subscriptions.clear()
    subscriptions.update({
        "sub-001": {
            "id": "sub-001",
            "user_id": "user-001",
            "plan_id": "plan-basic",
            "plan_name": "Basic",
            "status": "active",
            "payment_confirmed": True,
        },
        "sub-002": {
            "id": "sub-002",
            "user_id": "user-002",
            "plan_id": "plan-premium",
            "plan_name": "Premium",
            "status": "active",
            "payment_confirmed": True,
        },
    })

    # ── Invoices ─────────────────────────────────────────────────────────
    invoices.clear()
    invoices.update({
        "inv-001": {
            "id": "inv-001",
            "user_id": "user-001",
            "subscription_id": "sub-001",
            "amount": 9.99,
            "status": "paid",
            "created_at": "2026-07-01T10:00:00Z",
            # Internal fields (should be hidden in secure mode)
            "internal_user_id": "internal-ref-a-48291",
            "payment_processor_ref": "stripe_pi_3Qx9abc123def456",
            "cost_basis": 2.50,
            "debug_notes": "Applied early adopter discount. Original cost basis was $3.00.",
        },
        "inv-002": {
            "id": "inv-002",
            "user_id": "user-002",
            "subscription_id": "sub-002",
            "amount": 29.99,
            "status": "paid",
            "created_at": "2026-07-01T10:30:00Z",
            "internal_user_id": "internal-ref-b-58372",
            "payment_processor_ref": "stripe_pi_7Yz8mno789ghi012",
            "cost_basis": 8.00,
            "debug_notes": "Enterprise pilot user. Cost basis overridden by sales team.",
        },
        "inv-003": {
            "id": "inv-003",
            "user_id": "user-001",
            "subscription_id": "sub-001",
            "amount": 9.99,
            "status": "pending",
            "created_at": "2026-07-15T10:00:00Z",
            "internal_user_id": "internal-ref-a-48291",
            "payment_processor_ref": "stripe_pi_9Ab0pqr345stu678",
            "cost_basis": 2.50,
            "debug_notes": "Renewal invoice, auto-generated.",
        },
    })

    # ── Coupons ──────────────────────────────────────────────────────────
    coupons.clear()
    coupons.update({
        "coupon-001": {
            "id": "coupon-001",
            "code": "SAVE20",
            "discount_percent": 20,
            "active": True,
        },
        "coupon-002": {
            "id": "coupon-002",
            "code": "HALFOFF",
            "discount_percent": 50,
            "active": True,
        },
        "coupon-003": {
            "id": "coupon-003",
            "code": "EXPIRED10",
            "discount_percent": 10,
            "active": False,
        },
    })

    # ── Refunds ──────────────────────────────────────────────────────────
    refunds.clear()
    refunds.update({
        "ref-001": {
            "id": "ref-001",
            "invoice_id": "inv-001",
            "user_id": "user-001",
            "amount": 9.99,
            "reason": "Charged twice by mistake",
            "status": "pending",
        },
    })

    # ── Payments ─────────────────────────────────────────────────────────
    payments.clear()
    payments.update({
        "pay-001": {
            "id": "pay-001",
            "subscription_id": "sub-001",
            "user_id": "user-001",
            "amount": 9.99,
            "status": "confirmed",
            "invoice_id": "inv-001",
        },
        "pay-002": {
            "id": "pay-002",
            "subscription_id": "sub-002",
            "user_id": "user-002",
            "amount": 29.99,
            "status": "confirmed",
            "invoice_id": "inv-002",
        },
    })

    # ── Premium Features ─────────────────────────────────────────────────
    premium_features.clear()
    premium_features.update({
        "feat-001": {
            "id": "feat-001",
            "name": "Advanced Analytics Dashboard",
            "description": "Real-time analytics with custom reports and data export.",
            "tier": "premium",
        },
        "feat-002": {
            "id": "feat-002",
            "name": "Custom API Integrations",
            "description": "Connect MiniSub with your internal tools via webhooks and REST.",
            "tier": "premium",
        },
        "feat-003": {
            "id": "feat-003",
            "name": "Priority Support Channel",
            "description": "Direct access to engineering team within 1-hour SLA.",
            "tier": "premium",
        },
    })

    # ── Coupon Usage ─────────────────────────────────────────────────────
    coupon_usage.clear()

    print("[MiniSub] Database seeded successfully.")
    print(f"[MiniSub] {len(users)} users, {len(plans)} plans, {len(subscriptions)} subscriptions, {len(invoices)} invoices")
