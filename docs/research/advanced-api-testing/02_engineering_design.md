# Phase 2: Engineering Design and Scope Decision

## Introduction
Based on the Phase 0 audit and Phase 1 research, this document defines the engineering design for integrating PortSwigger's API Testing concepts into FlowShield. The architecture focuses on adding advanced, safe discovery capabilities and implementing a robust differential analysis verification system to maintain FlowShield's "Zero False Positive" ethos.

## Target Scanner Modules

The new capabilities will be compartmentalized into the following specific scanner engines located within `worker/app/engines/`.

### 1. API Documentation Discovery Engine
* **File:** `worker/app/engines/api_documentation_discovery.py`
* **Goal:** Discover exposed API documentation (e.g., Swagger UI, OpenAPI specs).
* **Implementation Strategy:** Execute a constrained dictionary attack (e.g., `/api`, `/docs`, `/swagger.json`) against the target base URL. Verification relies on checking the response for standard OpenAPI/Swagger signatures.

### 2. Undocumented Endpoint Discovery Engine
* **File:** `worker/app/engines/undocumented_endpoint_discovery.py`
* **Goal:** Identify legacy, admin, or internal endpoints not present in the provided specification.
* **Implementation Strategy:** Intelligently mutate known paths (e.g., swapping `/v2/` for `/v1/`, appending `/admin` or `/internal`). Verification uses the Differential Analyzer to distinguish a true hidden endpoint from a wildcard routing mechanism.

### 3. HTTP Method Discovery Engine
* **File:** `worker/app/engines/http_method_discovery.py`
* **Goal:** Detect endpoints accepting unauthorized or unintended HTTP methods (e.g., a `GET` endpoint processing a `PUT`).
* **Implementation Strategy:** Clone existing valid `GET` test cases but mutate the method to `POST`, `PUT`, `PATCH`, `DELETE`, and `OPTIONS`. Verification checks if the response code indicates success (e.g., `200 OK` or `201 Created`) rather than `405 Method Not Allowed`.

### 4. Content-Type Discovery Engine
* **File:** `worker/app/engines/content_type_discovery.py`
* **Goal:** Determine if alternative Content-Types (e.g., XML, URL-encoded) bypass security filters or trigger vulnerable parsers.
* **Implementation Strategy:** Take known JSON `POST/PUT` requests, convert the body to `application/x-www-form-urlencoded` or `application/xml`, and modify the headers. Verification ensures the backend processed the alternative format correctly.

### 5. Hidden Parameter Discovery Engine
* **File:** `worker/app/engines/hidden_parameter_discovery.py`
* **Goal:** Discover unlisted parameters (e.g., `admin=true`, `debug=1`) processed by the backend.
* **Implementation Strategy:** Inject a focused dictionary of common privilege-escalation parameters into query strings and JSON bodies. Verification strictly relies on differential analysis to see if the parameter changed the response structure compared to a baseline.

### 6. Enhanced Mass-Assignment Engine
* **File:** `worker/app/engines/mass_assignment.py`
* **Goal:** Upgrade the existing mass assignment module to verify state changes definitively.
* **Implementation Strategy:** Transition from single-request testing to a multi-step sequence. The engine will perform a state-modifying request (e.g., `PATCH {"is_premium": true}`) followed by a state-verifying `GET` request to confirm the object's properties were actually altered in the database.

### 7. Query-String SSPP Engine
* **File:** `worker/app/engines/sspp_query.py`
* **Goal:** Detect Server-Side Parameter Pollution in internal API query strings.
* **Implementation Strategy:** Inject delimiters (`%26`, `%23`, `%3F`) into reflected parameters. Verification requires comparing a safe, dummy parameter injection against a truncating injection to detect internal application logic shifts.

### 8. REST-Path SSPP Engine
* **File:** `worker/app/engines/sspp_path.py`
* **Goal:** Detect path traversal and SSPP within internal REST routing.
* **Implementation Strategy:** Inject URL-encoded slashes (`%2f`) and path traversal sequences (`..%2f`) into path parameters. Verification uses differential analysis to ensure standard path normalization behaves differently than a successful internal traversal.

### 9. Structured-Data SSPP Engine
* **File:** `worker/app/engines/sspp_structured.py`
* **Goal:** Detect parameter pollution inside internal JSON/XML payload construction.
* **Implementation Strategy:** Inject JSON delimiters (e.g., `","admin":true,"`) into string parameters. Verification focuses on detecting specific JSON parsing errors or explicit state changes that reflect the injected key.

### 10. Differential Response Analyzer
* **File:** `worker/app/engines/differential_analyzer.py`
* **Goal:** The core mathematical/structural engine for comparing HTTP responses.
* **Implementation Strategy:** Compare a baseline response against a mutated response by calculating structural similarity. It must intelligently filter out dynamic data (e.g., CSRF tokens, timestamps, UUIDs) to prevent false positives.

### 11. Advanced Finding Verifier
* **File:** `worker/app/engines/advanced_verification.py`
* **Goal:** Aggregate and evaluate the results of the complex discovery engines.
* **Implementation Strategy:** Wraps or integrates with the existing `verification.py`. It orchestrates the calls to the `differential_analyzer.py` and assigns confidence levels to the generated `Finding` records.

## Integration Architecture & Data Flow

1. **Test Generation:** The new engines (1-9) will hook into the `generate_all_tests` function in `worker/app/engines/test_generator.py`.
2. **Execution:** The execution phase in `main.py` requires minimal changes, as it already supports running generated `TestCase` schemas.
3. **Verification Phase:** Instead of simple status code logic, `advanced_verification.py` will process the `TestExecution` records, heavily relying on `differential_analyzer.py` to confirm vulnerabilities.

## Scope Constraints
To protect the existing Scan Budget (`max_total_requests`), the wordlists utilized by the Documentation, Endpoint, and Parameter discovery engines will be strictly minimized (e.g., top 10 most impactful mutations) rather than utilizing exhaustive fuzzing lists.
