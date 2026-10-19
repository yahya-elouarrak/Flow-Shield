# FlowShield Security Report

**Automated API Security Assessment**

## 1. Metadata
- **Project:** {{ project.name }}
- **Target URL:** {{ project.base_url }}
- **Environment:** {% if project.environment_type == 'bug_bounty' %}Bug Bounty (Safe Mode){% else %}Staging / Test{% endif %}
- **Scan ID:** {{ scan.id }}
- **Date:** {{ scan.started_at }}
- **ROE Confirmed:** {{ 'Yes' if scan.roe_confirmed else 'No' }}
{% if project.environment_type == 'bug_bounty' %}
- **Mode:** {% if scan.dry_run %}Dry Run{% else %}Live Execution{% endif %}
- **Rules of Engagement:** Strict Scope, No Destructive Testing, No State Changes
{% endif %}

## 2. Executive Summary
- **Endpoints Parsed:** {{ total_endpoints }}
- **Tests Generated:** {{ total_tests }}
{% if project.environment_type == 'bug_bounty' %}
- **Request Budget Used:** {{ scan.events|selectattr("phase", "equalto", "executing")|selectattr("message", "match", "Executed.*requests total")|map(attribute="message")|first | default("Unknown") }} / {{ target_config.max_total_requests }} Max
{% endif %}
- **Total Findings:** {{ total_findings }}
- **Overall Risk:** {{ overall_risk }}

This report details the findings from an automated API security scan targeting {{ project.name }}. The scan performed authenticated grey-box testing, focusing on Business Logic Vulnerabilities such as BOLA (Broken Object Level Authorization), BFLA (Broken Function Level Authorization), and Mass Assignment.

## 3. Testing Scope
**Allowed Hosts:**
{% for host in target_config.allowed_hosts %}
- `{{ host }}`
{% else %}
- Any
{% endfor %}

**Allowed Paths:**
{% for path in target_config.allowed_paths %}
- `{{ path }}`
{% else %}
- `/*`
{% endfor %}

## 4. Methodology
- **Grey-box testing:** The scanner utilizes an OpenAPI/Swagger definition to understand the API surface.
- **Multi-role testing:** Test cases are executed under different user contexts (e.g., Customer vs. Admin) to identify vertical and horizontal privilege escalation.
- **Deterministic engines:** Specialized heuristic engines are used to automatically find and exploit BOLA, BFLA, and Mass Assignment flaws.
- **Evidence-based verification:** Findings are only confirmed if the server responds with definitive proof of vulnerability (e.g., leaking sensitive data from another user's object).

## 5. Findings Summary
{% if findings %}
| Severity | Category | Vulnerability | Endpoint | Confidence |
| --- | --- | --- | --- | --- |
{% for f in findings %}
| {{ f.severity }} | {{ f.category }} | {{ f.title }} | `{{ f.endpoint_method }} {{ f.endpoint_path }}` | {{ f.confidence }} |
{% endfor %}
{% else %}
No vulnerabilities were found during this scan.
{% endif %}

## 6. Detailed Findings
{% if findings %}
{% for f in findings %}
### {{ loop.index }}. {{ f.title }}
- **Severity:** {{ f.severity }}
- **Confidence:** {{ f.confidence }}
- **Category:** {{ f.category }}
- **Endpoint:** `{{ f.endpoint_method }} {{ f.endpoint_path }}`
- **Attacker Role:** {{ f.attacker_role or "None" }}

**Description**
{{ f.description }}

**Impact**
{{ f.impact }}

**Remediation**
{{ f.remediation }}

{% if f.evidence %}
**Evidence Summary**
{{ f.evidence.proof_text }}

**Request**
```http
{{ f.evidence.request_method }} {{ f.evidence.request_url }}
{% if f.evidence.request_body_redacted %}

{{ f.evidence.request_body_redacted | tojson(indent=2) }}
{% endif %}
```

**Response ({{ f.evidence.response_status }})**
```json
{% if f.evidence.response_body_redacted %}
{{ f.evidence.response_body_redacted | tojson(indent=2) }}
{% else %}
Empty Response
{% endif %}
```
{% endif %}
---
{% endfor %}
{% endif %}

## 7. General Recommendations
- **Enforce Ownership Checks (BOLA):** Ensure that every endpoint querying or modifying a specific object validates that the authenticated user is the legitimate owner of that object.
- **Enforce Function-Level Access Control (BFLA):** Require strict Role-Based Access Control (RBAC) at the route handler level, rather than relying on UI hiding.
- **Prevent Mass Assignment:** Do not blindly bind request payloads to database models. Use explicit Data Transfer Objects (DTOs) and allowlists.
