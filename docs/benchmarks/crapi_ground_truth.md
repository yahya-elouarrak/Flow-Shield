# crAPI — Ground-Truth Vulnerability Matrix

> Built from the OWASP crAPI challenge documentation.

## Vulnerability Matrix

| Vuln ID | Class | Endpoint(s) | Expected Exploit Behavior |
|---|---|---|---|
| **CR-01** | **BOLA / IDOR** | `GET /identity/api/v2/vehicle/{vehicle_id}/location` | Any authenticated user can read the location of any vehicle by supplying its ID. |
| **CR-02** | **BOLA / IDOR** | `GET /workshop/api/merchant/report?report_id={report_id}` | Users can access mechanic reports of other users by changing the `report_id`. |
| **CR-03** | **Business Logic / Mass Assignment** | `POST /workshop/api/shop/orders` | Users can supply a negative `quantity` to get an item for free and increase their balance. |
| **CR-04** | **BFLA** | `DELETE /identity/api/v2/user/videos/{video_id}` | Users can delete videos of other users, or access admin-only endpoints. |
| **CR-05** | **NoSQL Injection** | `POST /workshop/api/merchant/contact_mechanic` (or coupons) | Inject NoSQL operators to bypass coupon code verification. |
| **CR-06** | **Excessive Data Exposure** | `GET /community/api/v2/community/posts/recent` | Exposes internal `vehicleid` and full names of authors, which facilitates CR-01. |
| **CR-07** | **JWT Vulnerabilities** | `GET /identity/api/v2/user/dashboard` | Does not validate JWT signature, accepting forged tokens if `sub` is changed. |

## FlowShield Detection Expectations

| Category | FlowShield Engine | Expected Detection |
|---|---|---|
| BOLA (CR-01, CR-02) | `bola.py` | Should detect if it can discover valid `vehicle_id`s or `report_id`s (currently limited by hardcoded IDs). |
| Mass Assignment (CR-03) | `mass_assignment.py` | May not detect negative quantities since MA engine focuses on object properties like `role` and `balance`. The `workflow.py` engine tests negative quantities but only on specific hardcoded endpoints. |
| BFLA (CR-04) | `bfla.py` | Should detect if admin endpoints or cross-user deletes are properly instrumented. |

## Seed Data Reference

*To be provisioned before scanning.*
| Account | Role |
|---|---|
| attacker@example.com | customer |
| victim@example.com | customer |
| admin@example.com | admin |
