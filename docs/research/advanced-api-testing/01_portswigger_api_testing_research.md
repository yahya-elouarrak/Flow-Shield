# PortSwigger API Testing Research

**Access Date:** 2026-08-13
**Sources Consulted:** Official PortSwigger Web Security Academy - API Testing Topic (https://portswigger.net/web-security/api-testing)

## Introduction
This document captures the core concepts from the PortSwigger API Testing learning path to serve as the foundation for FlowShield's advanced discovery and parameter testing engines. The objective is to translate these manual hacking techniques into safe, automatable scanning strategies.

## Concepts & Matrices

### 1. Exposed API Documentation
**Vulnerability Concept:** Developers often leave API documentation (Swagger, OpenAPI, GraphQL endpoints, WADL) accessible in production. This provides attackers with a complete map of the API's attack surface, including hidden parameters and administrative endpoints.
**Prerequisites:** Unauthenticated or authenticated access to documentation endpoints.
**Business Impact:** Information disclosure that accelerates subsequent attacks.
**Remediation:** Disable or strictly restrict access to documentation endpoints in production.

| Concept | Discovery signal | Safe mutation | Verification | False positives | Lab scenario | Scanner feasibility |
|---|---|---|---|---|---|---|
| Exposed API Docs | HTTP 200 on common doc paths (`/api`, `/swagger-ui.html`, `/openapi.json`) | GET requests to common documentation wordlist | Response body contains Swagger/OpenAPI signature or JSON schema structure | Catch-all endpoints returning 200 with generic HTML, WAF blocks returning 200 | *Exploiting an API by finding documentation* | High - simple directory brute-force |

### 2. Undocumented / Unused API Endpoints
**Vulnerability Concept:** APIs may contain legacy versions (`/v1/` instead of `/v2/`), unused administrative endpoints, or internal-only routes that lack proper access controls because developers assume they are unknown.
**Prerequisites:** Knowledge of the API structure and common naming conventions.
**Business Impact:** Unauthorized access to sensitive actions (e.g., deleting users, bypassing payments).
**Remediation:** Remove unused code and ensure authorization is consistently applied to all routes.

| Concept | Discovery signal | Safe mutation | Verification | False positives | Lab scenario | Scanner feasibility |
|---|---|---|---|---|---|---|
| Undocumented Endpoints | 200 OK or 401/403 on guessed endpoint (when 404 is expected) | Replace `/v2/` with `/v1/`, append `/admin` or `/internal` to known paths | Compare response of guessed path vs guaranteed non-existent path (differential analysis) | Wildcard routing returning 200 for any path | *Finding and exploiting an unused API endpoint* | Medium - requires intelligent wordlists and differential analysis |

### 3. HTTP Method Discovery
**Vulnerability Concept:** An endpoint designed for a `GET` request might also accept a `POST`, `PUT`, `PATCH`, or `DELETE` method. If access controls are only enforced on the `GET` method, sending a different method could bypass authorization.
**Prerequisites:** A known valid endpoint.
**Business Impact:** Bypassing access controls to modify or delete data.
**Remediation:** Explicitly reject unsupported HTTP methods (return 405 Method Not Allowed) and apply auth checks uniformly.

| Concept | Discovery signal | Safe mutation | Verification | False positives | Lab scenario | Scanner feasibility |
|---|---|---|---|---|---|---|
| Method Discovery | Non-405/501 response for non-standard methods (e.g., sending PATCH to a GET endpoint) | Send identical request but swap method (GET, POST, PUT, DELETE, PATCH, OPTIONS) | Response code indicates action (e.g., 201 Created) or OPTIONS returns 'Allow' header | 403 Forbidden might just mean method is accepted but user unauthorized | N/A (General Concept) | High - easy to iterate methods per endpoint |

### 4. Content-Type Discovery
**Vulnerability Concept:** Endpoints might behave differently based on the `Content-Type` provided (e.g., XML instead of JSON, URL-encoded instead of JSON). This can bypass WAF rules or trigger different backend parsing logic, potentially leading to XXE or parameter pollution.
**Prerequisites:** Endpoint accepts input.
**Business Impact:** Bypassing security filters, triggering vulnerable parsers.
**Remediation:** Strictly enforce the expected `Content-Type` header (e.g., `application/json`) and reject others.

| Concept | Discovery signal | Safe mutation | Verification | False positives | Lab scenario | Scanner feasibility |
|---|---|---|---|---|---|---|
| Content-Type Discovery | 200 OK after changing Content-Type | Convert JSON to XML/Form-encoded and modify Content-Type header | Backend processes the payload identically to the original Content-Type | Server ignores Content-Type and processes raw body anyway | N/A (General Concept) | High - standard format translations |

### 5. Hidden Parameter Discovery & Mass Assignment
**Vulnerability Concept:** Mass assignment occurs when a framework automatically binds HTTP parameters directly to an internal object without filtering. Attackers can discover "hidden" parameters (e.g., `is_admin`, `discount`) and inject them.
**Prerequisites:** A state-modifying endpoint (POST, PUT, PATCH).
**Business Impact:** Privilege escalation, bypassing business logic (e.g., modifying prices).
**Remediation:** Use explicit DTOs (Data Transfer Objects) and never bind raw input directly to internal database models.

| Concept | Discovery signal | Safe mutation | Verification | False positives | Lab scenario | Scanner feasibility |
|---|---|---|---|---|---|---|
| Mass Assignment | Response changes, or object state changes after injecting a guessed parameter | Add `{"role":"admin"}`, `{"is_admin":true}` to JSON bodies | Verify via a subsequent GET request if the state actually changed | 200 OK but parameter is silently ignored by the backend | *Exploiting a mass assignment vulnerability* | High - injecting common property lists and checking state |

### 6. Server-Side Parameter Pollution (SSPP) - Query String
**Vulnerability Concept:** SSPP occurs when an application embeds user input into a server-side request to an internal API without proper encoding. By injecting query delimiters (`#`, `&`, `=`), attackers can override or append parameters to the internal request.
**Prerequisites:** Input field that is reflected in a server-side API call.
**Business Impact:** Bypassing business logic, modifying internal API calls.
**Remediation:** Strictly URL-encode all user input before embedding it in internal API requests.

| Concept | Discovery signal | Safe mutation | Verification | False positives | Lab scenario | Scanner feasibility |
|---|---|---|---|---|---|---|
| Query SSPP | Anomalous behavior or errors when injecting `%23` (#), `%26` (&), or `%3F` (?) | Append `%26admin=true` to an input field | Injecting a safe parameter (e.g. `&x=y`) returns normal response, while truncated `foo%23` changes results | WAF blocking special characters | *Exploiting server-side parameter pollution in a query string* | Medium - requires differential responses |

### 7. Server-Side Parameter Pollution (SSPP) - REST Path
**Vulnerability Concept:** Similar to query-string SSPP, but occurs when input is placed into a URL path of an internal API. Using path traversal (`../`) or URL-encoded slashes (`%2f`), attackers can navigate out of the intended internal endpoint.
**Prerequisites:** Input field placed into an internal REST path.
**Business Impact:** Accessing unauthorized internal endpoints.
**Remediation:** Validate input against a strict allowlist; URL-encode input safely.

| Concept | Discovery signal | Safe mutation | Verification | False positives | Lab scenario | Scanner feasibility |
|---|---|---|---|---|---|---|
| REST Path SSPP | 404 or structural errors when injecting URL encoded slashes/traversals | Inject `..%2f` or `%2f..%2f` | `input/..%2finput` yields the same result as `input` (path normalization) | Strict routing returning 400 for any special character | *Exploiting server-side parameter pollution in a REST URL* | Medium - requires differential responses and careful URL encoding |

### 8. Server-Side Parameter Pollution (SSPP) - Structured Formats
**Vulnerability Concept:** If user input is embedded directly into JSON/XML payloads sent to an internal API, injecting JSON delimiters (e.g., `","admin":true,"`) can manipulate the internal JSON structure.
**Prerequisites:** Input field embedded into an internal JSON/XML request.
**Business Impact:** Privilege escalation, manipulating backend data.
**Remediation:** Use proper JSON serialization libraries; never concatenate strings to form JSON.

| Concept | Discovery signal | Safe mutation | Verification | False positives | Lab scenario | Scanner feasibility |
|---|---|---|---|---|---|---|
| Structured SSPP | JSON parsing errors when injecting `"`, `{`, `}` | Inject `","test":"1` into a string parameter | The application state reflects the injected parameter | Syntax errors caught by frontend/gateway before reaching internal API | N/A (General Concept) | Medium - error/differential based |

### Safe Verification Principles
- **Avoid destructive actions**: Tests should not use DELETE, drop databases, or change critical configurations (e.g., passwords).
- **Differential Analysis**: A core tenet for automation. Instead of relying purely on status codes, the scanner must compare the response of a manipulated request against a known baseline (e.g., injecting a dummy parameter vs. injecting a logic-altering parameter).
- **State Validation**: For mass assignment, sending a `POST/PUT` is not enough. The scanner MUST perform a follow-up `GET` to verify if the object's state actually changed.

## Vulnerable API Local Representation Strategy
To build this into FlowShield's `vulnerable-saas`:
1. **API Docs**: Expose a `/swagger.json` path that reveals an undocumented endpoint.
2. **Hidden Endpoint**: Create a `/v1/internal/admin/reset_invoices` endpoint that lacks auth.
3. **HTTP Methods**: Allow an invoice update via `POST` when it's supposed to be restricted to `PUT`.
4. **Mass Assignment**: The user profile `PATCH` endpoint should allow modifying an `is_premium` boolean.
5. **SSPP**: An endpoint that fetches a user's subscription internally via a constructed URL. Injecting `&discount=100` allows bypassing payment requirements.

## Next Steps
This research proves that a significant portion of API testing involves intelligent mutation and differential analysis. This will guide the Phase 2 engineering design, dictating the creation of specialized engines and a verification module that can handle complex response comparisons.
