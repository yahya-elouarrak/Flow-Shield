# MiniSub SaaS — Ground-Truth Vulnerability Matrix

> Built from direct source code analysis of the vulnerable-saas directory before any FlowShield scan.
> All vulnerabilities are gated behind `settings.VULNERABLE_MODE == True`.

## Vulnerability Matrix

| Vuln ID | Class | Endpoint(s) | Expected Exploit Behavior | Source Reference |
|---|---|---|---|---|
| **MS-01** | **BOLA / IDOR + Excessive Data Exposure** | `GET /invoices/{invoice_id}` | Any authenticated user can read any invoice by ID. No ownership check. Also leaks internal fields: `internal_user_id`, `payment_processor_ref`, `cost_basis`, `debug_notes`. | invoice_routes.py L30-58 |
| **MS-02** | **BFLA** | `GET /admin/users` | Any authenticated user (customer, support) can list all users — no admin role check in vulnerable mode. | admin_routes.py L12-35 |
| **MS-03** | **BFLA + Mass Assignment** | `PATCH /admin/users/{user_id}` | Any authenticated user can update any user's `role` and `subscription_status` fields — privilege escalation via mass assignment. No admin role check. | admin_routes.py L38-81 |
| **MS-04** | **BFLA** | `POST /support/refunds/{refund_id}/approve` | Any authenticated user can approve refunds — no role check for support/admin. | refund_routes.py L49-71 |
| **MS-05** | **Business Logic — Price Manipulation** | `POST /payments/checkout` | Client-supplied `amount` is accepted directly. Attacker can set `amount: 0.01` or `amount: -100` to pay less or negative amounts. | payment_routes.py L12-57 |
| **MS-06** | **Business Logic — Payment Bypass** | `POST /subscriptions/activate` | Subscription can be activated without `payment_confirmed == True`, bypassing the payment step entirely. | subscription_routes.py L56-89 |
| **MS-07** | **Business Logic — Coupon Reuse** | `POST /coupons/apply` | Same coupon can be reused unlimited times by the same user (no usage tracking enforcement). | coupon_routes.py L11-65 |
| **MS-08** | **Business Logic — Negative Refund** | `POST /refunds/request` | Negative refund amounts accepted (no validation). Attacker can submit `amount: -1000` to extract money. | refund_routes.py L12-46 |
| **MS-09** | **Business Logic — Subscription Bypass** | `GET /premium/features` | Premium features returned regardless of subscription status or plan. No authorization check against user's subscription. | premium_routes.py L12-29 |
| **MS-10** | **SSPP (Server-Side Parameter Pollution)** | `GET /internal/subscription_check` | Three SSPP variants: (a) Query parameter pollution via `%26discount` injection → forces `discount=100`; (b) Structured injection via `",\"admin\":true` → returns `admin: true`; (c) Path traversal via `%2f..%2f` → returns `admin_root`. | sspp_routes.py L7-34 |
| **MS-11** | **Information Disclosure** | `GET /debug/status` | Undocumented endpoint (`include_in_schema=False`), no authentication required. Returns internal metrics. | sspp_routes.py L36-41 |

## Summary by Category

| Category | Count | IDs |
|---|---|---|
| BOLA / IDOR | 1 | MS-01 |
| BFLA | 3 | MS-02, MS-03, MS-04 |
| Mass Assignment | 1 | MS-03 (overlaps with BFLA) |
| Business Logic | 5 | MS-05, MS-06, MS-07, MS-08, MS-09 |
| SSPP | 1 | MS-10 (3 variants) |
| Information Disclosure | 1 | MS-11 |
| **Total Unique** | **11** | — |

## FlowShield Detection Expectations

| Category | FlowShield Engine | Expected Detection |
|---|---|---|
| BOLA (MS-01) | `bola.py` — path parameter ID swapping | Should detect (endpoint has `{invoice_id}` param) |
| BFLA (MS-02, MS-03, MS-04) | `bfla.py` — keyword matching (`admin`, `support`, `refund`, `role`) | Should detect (paths contain `admin`, `support/refunds`) |
| Mass Assignment (MS-03) | `mass_assignment.py` — injects `role: admin`, `balance: 999999` etc. | Partial — targets `PATCH /admin/users/{user_id}` but may not verify correctly |
| Business Logic (MS-05 to MS-09) | `workflow.py` | Depends on workflow engine coverage |
| SSPP (MS-10) | `sspp_query.py`, `sspp_path.py`, `sspp_structured.py` | Should detect (dedicated engines exist) |
| Info Disclosure (MS-11) | `undocumented_endpoint_discovery.py` | May miss (`/debug/status` is not in OpenAPI schema) |

## Seed Data Reference

| Account | Email | Role | User ID |
|---|---|---|---|
| customer_a | `customer_a@example.com` | customer | `user-001` |
| customer_b | `customer_b@example.com` | customer | `user-002` |
| support | `support@example.com` | support | `user-003` |
| admin | `admin@example.com` | admin | `user-004` |

**Password for all accounts:** `Password123`

| Resource | ID | Owner |
|---|---|---|
| Invoice 1 | `inv-001` | user-001 |
| Invoice 2 | `inv-002` | user-002 |
| Invoice 3 | `inv-003` | user-001 |
| Subscription 1 | `sub-001` | user-001 |
| Subscription 2 | `sub-002` | user-002 |
| Refund 1 | `ref-001` | user-001 |
| Coupon SAVE20 | `coupon-001` | — |
| Coupon HALFOFF | `coupon-002` | — |
| Coupon EXPIRED10 | `coupon-003` | — (inactive) |
