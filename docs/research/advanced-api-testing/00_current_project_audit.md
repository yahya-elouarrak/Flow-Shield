# Phase 0: Current Project Audit

## 1. Current Working Architecture
FlowShield uses a microservices architecture orchestrated via Docker Compose:
- **Frontend**: Next.js (App Router), provides the UI for project management, configuration, and report viewing.
- **Backend**: FastAPI (Python), exposes REST endpoints for managing projects, OpenAPI parsing, role/account configurations, and reporting. Uses Alembic for migrations.
- **Worker**: Python/HTTPX, polls for pending ScanJobs. Handles the core scanning lifecycle: Loading, Validating, Planning, Executing, Verifying, and Reporting. Supports an AI planner via Ollama.
- **Database**: PostgreSQL, stores configuration, test accounts, scan jobs, endpoints, test executions, and findings.
- **Vulnerable Target**: `vulnerable-saas`, a custom seeded API (FastAPI) containing intentional logic flaws for demonstration and testing.

## 2. Current Working Features
- OpenAPI/Swagger documentation import.
- Project and scope configuration.
- Role and test account management.
- Authentication configuration (JWT Bearer tokens, custom login endpoints).
- Multi-role, deterministic security test generation.
- Request rate limiting and safety controls (e.g., maximum requests).
- Result verification engine.
- Report generation.

## 3. Current Scanner Engines
The worker currently implements the following scanning logic in `worker/app/engines/`:
- **BOLA (Broken Object Level Authorization)** (`bola.py`)
- **BFLA (Broken Function Level Authorization)** (`bfla.py`)
- **Mass Assignment** (`mass_assignment.py`)
- **Workflow & AI Planner** (`workflow.py`, `ai_planner.py`)
- **Test Generation** (`test_generator.py`)
- **Verification Engine** (`verification.py`)

## 4. Existing Database Entities
Located in `backend/app/models/`:
- `Project`, `TargetConfig`, `Endpoint`, `Account`, `AuthConfig`
- `ScanJob`, `ScanEvent`, `TestCase`, `TestExecution`
- `Finding`, `Report` (inferred from routing)

## 5. Existing API Routes
- **Backend API (`backend/app/api/`)**: `routes_projects.py`, `routes_openapi.py`, `routes_auth.py`, `routes_scans.py`, `routes_findings.py`, `routes_reports.py`.
- **Vulnerable SaaS (`vulnerable-saas/app/routes/`)**: `auth`, `admin`, `coupon`, `invoice`, `payment`, `premium`, `refund`, `subscription`, `user`.

## 6. Current Vulnerable Lab Scenarios
The `vulnerable-saas` includes seeded accounts (customer_a, customer_b, admin) and routes for managing subscriptions, invoices, and payments. The deliberate vulnerabilities align with the current BOLA, BFLA, and Mass Assignment tests.

## 7. Technical Debt & Integration Risks
- **Scan Budget Exhaustion**: Fuzzing parameters and endpoints for advanced API discovery can quickly consume `max_total_requests` set in `TargetConfig`.
- **AI Dependencies**: Fallbacks must be strictly maintained to ensure the deterministic engines function perfectly without Ollama.
- **Synchronous Execution**: The worker processes requests synchronously (with delays). Mass testing for parameter pollution might drastically increase scan times.

## 8. Exact Extension Points for New Engines
To integrate the PortSwigger API Testing methodology:
- `worker/app/engines/test_generator.py`: To generate test cases for parameter pollution, HTTP method discovery, and undocumented endpoints.
- `worker/app/engines/verification.py`: To implement the differential analysis required to verify if a manipulated request fundamentally alters the response.
- `worker/app/main.py`: To orchestrate the new discovery steps during Phase 2 (Loading Endpoints) and Phase 5 (Planning).
- `vulnerable-saas`: New routes or modified existing routes to serve as test targets for the new vulnerabilities.

## 9. Regression Risks
- Modifying `test_generator.py` or the `TestCase` schema could break the existing BOLA and BFLA engines.
- Modifying `execute_http_request` (in `worker/app/http/client.py`) to support different Content-Types or malformed parameter pollution could introduce bugs into normal standard REST requests.

## 10. Proposed Implementation Order
1. **Phase 1**: Official research on PortSwigger API security modules.
2. **Phase 2**: Detailed engineering design and architecture scoping.
3. **Phase 3**: Core engine implementation (Discovery & Structure).
4. **Phase 4**: Core engine implementation (Parameter Pollution & Mass Assignment).
5. **Phase 5**: Update `vulnerable-saas` to cover the new scenarios.
6. **Phase 6**: Verification & Differential Analysis enhancements.
7. **Phase 7**: End-to-end testing and QA.
