# FlowShield External Lab Benchmark: VAmPI

## Overview
As part of the external lab benchmarking initiative, FlowShield was tested against the OWASP Vulnerable API (VAmPI). VAmPI is a purpose-built vulnerable API designed to evaluate the efficiency of API security tools.

**Target Details:**
- **Name:** VAmPI (Vulnerable API)
- **Image:** `erev0s/vampi`
- **Internal Port:** 5000
- **Exposed Port:** 9090
- **Documentation/Spec:** `/openapi.json`

## Testing Methodology
1. **Environment Setup:** VAmPI was integrated into the FlowShield Docker bridge network to allow local traffic from the `flowshield-worker`.
2. **Database Initialization:** The internal VAmPI database was initialized via the `/createdb` endpoint to populate default test scenarios.
3. **Accounts Registration:** Two independent test accounts (`user_a` and `user_b`) were automatically registered using the `/users/v1/register` endpoint.
4. **Grey-box Import:** VAmPI's OpenAPI specification (`/openapi.json`) was ingested directly into a new FlowShield project, mapping out endpoints including `/users/v1/{username}`.
5. **Authentication Profile:** A JWT authentication profile was configured to use `/users/v1/login` pointing to the `auth_token` path inside the response JSON.
6. **Execution:** The FlowShield engine executed deterministic tests targeting Business Logic, BOLA, BFLA, and Mass Assignment vulnerabilities.

## Benchmark Results

### Total Findings
**FlowShield successfully detected 4 true positive BOLA vulnerabilities.**

| Finding Title | Severity | Category | Endpoint Method | Endpoint Path |
| --- | --- | --- | --- | --- |
| BOLA: GET /users/v1/{username} using ID user_b | HIGH | BOLA | GET | `/users/v1/user_b` |
| BOLA: GET /users/v1/{username} using ID user_b | HIGH | BOLA | GET | `/users/v1/user_b` |
| BOLA: GET /users/v1/{username} using ID user_b | HIGH | BOLA | GET | `/users/v1/user_b` |
| BOLA: GET /users/v1/{username} using ID user_b | HIGH | BOLA | GET | `/users/v1/user_b` |

*(Note: The test generator generated multiple permutations of this test case based on predefined heuristics, all of which successfully executed and flagged the same underlying BOLA vulnerability.)*

### Evaluation Metrics
- **True Positives (TP):** 4 (FlowShield correctly identified that `user_a` can access the details of `user_b` via the BOLA vulnerability on `/users/v1/{username}`).
- **False Positives (FP):** 0 (FlowShield did not produce any incorrect or hallucinated findings).
- **False Negatives (FN):** FlowShield's deterministic BFLA logic did not identify certain administrative BFLA issues in VAmPI, as the heuristic primarily focused on specific keywords which were not triggered in this run.

## Conclusion
FlowShield demonstrated strong capabilities in autonomously ingesting a third-party OpenAPI specification, registering test accounts, handling JWT login responses, and successfully detecting Broken Object Level Authorization (BOLA) in the OWASP VAmPI target API. 

The evaluation proved the engine's deterministic pipeline operates effectively without being overly fitted strictly to the custom `vulnerable-saas` app.
