# FlowShield End-to-End Demo Script

This script provides a step-by-step walkthrough for demonstrating FlowShield's capabilities during a Project Defense or technical evaluation.

## Environment Preparation

Before starting the demo, ensure the environment is clean:
```bash
docker compose down -v
docker compose up --build -d
```
This guarantees a fresh database and rebuilt containers.

---

## 1. Project Initialization

1. Open the dashboard at `http://localhost:3000`.
2. Click **New Project**.
3. **Name:** `MiniSub SaaS API Test`
4. **Target API:** `http://localhost:9000` *(FlowShield automatically resolves this to the internal vulnerable-saas container)*
5. **Environment:** `Local / Lab`
6. Click **Create Project**.

---

## 2. API Discovery (OpenAPI Import)

1. On the Project Overview, locate the **OpenAPI Schema** section.
2. Select **Import URL**.
3. **URL:** `http://localhost:9000/openapi.json`
4. Click **Import**.
5. *Talking Point:* Explain how FlowShield parses the spec to inventory 19 endpoints, identifying path parameters, schemas, and potential sensitive fields before the scan even starts.

---

## 3. Account & Role Mapping

FlowShield uses multi-role testing to find BOLA/BFLA vulnerabilities. We will configure 4 accounts seeded in our vulnerable target.

1. Navigate to **Settings > Roles**.
2. Add three roles:
   - `customer` (Level 10)
   - `support` (Level 50)
   - `admin` (Level 100)
3. Navigate to **Settings > Test Accounts**. Add the following accounts:
   - **Label:** `customer_a` | **Role:** `customer` | **Username:** `customer_a@example.com` | **Password:** `Password123`
   - **Label:** `customer_b` | **Role:** `customer` | **Username:** `customer_b@example.com` | **Password:** `Password123`
   - **Label:** `support` | **Role:** `support` | **Username:** `support@example.com` | **Password:** `Password123`
   - **Label:** `admin` | **Role:** `admin` | **Username:** `admin@example.com` | **Password:** `Password123`
4. *Talking Point:* Emphasize that FlowShield handles authentication dynamically so it can hot-swap tokens to test cross-account authorization.

---

## 4. Authentication Configuration

1. Navigate to **Settings > Target & Auth**.
2. Scroll to the **Authentication Configuration** section.
3. Configure the JWT login workflow:
   - **Login Endpoint:** `/auth/login`
   - **Username Field:** `email`
   - **Password Field:** `password`
   - **Token JSON Path:** `access_token`
   - **Header Template:** `Authorization: Bearer {token}`
4. Save the configuration.

---

## 5. Scope & Safety Configuration

1. In **Settings > Target & Auth**, locate the **Safety & Scope** section.
2. Ensure the following rules are set to prevent accidental damage:
   - **Allowed Hosts:** `localhost:9000` (or `vulnerable-saas`)
   - **Allow Destructive Tests (DELETE):** Unchecked
   - **Allow Payment Execution:** Unchecked
3. *Talking Point:* Discuss FlowShield's safety profile, explaining why it's safe to run in staging or even production environments when correctly scoped.

---

## 6. Scan Execution

1. Navigate to the **New Scan** page.
2. Select the vulnerability engines:
   - ✅ BOLA (Broken Object Level Authorization)
   - ✅ BFLA (Broken Function Level Authorization)
   - ✅ Mass Assignment
3. Enable **AI-Assisted Reasoning** (if Ollama is running). *Note: If Ollama is offline, FlowShield gracefully falls back to deterministic tests.*
4. Check the **Rules of Engagement** box.
5. Click **Launch Scan**.
6. *Talking Point:* Explain the asynchronous worker architecture. The scan goes through strictly defined phases: Planning, Executing, Verifying, and Reporting.

---

## 7. Findings & Evidence Verification

1. Once the scan completes, navigate to **Findings**.
2. You will observe multiple critical and high vulnerabilities detected in the `MiniSub SaaS`:
   - **BOLA:** `customer_a` successfully accessing `customer_b`'s invoices.
   - **BFLA:** `customer` successfully executing an admin-only endpoint.
   - **Mass Assignment:** `customer` elevating privileges by injecting `role: admin` in a profile update.
3. Click on a specific finding to view the **Evidence**.
4. *Talking Point:* Show how the exact HTTP request and response are captured. Point out that **passwords, tokens, and PII are redacted**, proving the platform is safe for compliance. Mention the "Zero False Positives" verification engine.

---

## 8. Reporting

1. Navigate to **Reports**.
2. Click **HTML Report**.
3. Open the downloaded file to showcase the professional, standalone vulnerability report suitable for developers and management.
4. *Talking Point:* Conclude by mentioning the JSON export capability for CI/CD integration and Jira automation.
