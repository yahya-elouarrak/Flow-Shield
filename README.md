<div align="center">

<img src="frontend/public/images/logo_lockup_transparent.png" alt="FlowShield Logo" width="420" />

<br />
<br />

![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Frontend-Next.js_14-000000?style=flat-square&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/Language-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Language-Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL_15-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Orchestration-Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![OWASP](https://img.shields.io/badge/Security-OWASP_API_Top_10-E24329?style=flat-square)

**Automated API Security Testing Platform Specializing in Authorization Logic Flaws**

*Detecting BOLA, BFLA, Mass Assignment, and Parameter Pollution with a Zero False Positive Verification Engine.*

[Quick Start](#-quick-start) • [Architecture](#-architecture) • [Security Engines](#-detection-engines) • [Demo Walkthrough](#-demo-walkthrough) • [AI Configuration](#-ai-planner-configuration)

</div>

---

## 📌 Overview

**FlowShield** is an automated microservice security testing platform designed to discover complex **business logic and authorization vulnerabilities** in REST APIs—the critical flaws traditional DAST scanners consistently miss.

By parsing **OpenAPI 3.0 / Swagger** specifications, FlowShield automatically maps API surfaces, configures multi-tenant test roles, generates contextual attack payloads, and executes non-destructive security scans with strict **Zero False Positive** multi-stage verification.

### Key Capabilities
- **Cross-Role Authorization Testing**: Automated cross-tenant matrix evaluation for BOLA/IDOR and BFLA privilege escalation.
- **16 Specialized Scan Engines**: Deterministic fuzzing, parameter pollution (SSPP), hidden endpoint/parameter discovery, and verb tampering.
- **Dual AI Test Planner**: Fast cloud reasoning via **Groq** (`llama-3.1-8b-instant`) or 100% offline private execution via **Ollama** (`qwen2.5-coder:7b`).
- **Zero Token Exposure**: AI models only receive sanitized schema metadata (method, route, schema keys)—credentials and auth tokens are never exposed.
- **Built-in Vulnerable SaaS ("MiniSub")**: Out-of-the-box target seeded with 10+ intentional authorization flaws for immediate demonstration.
- **Enterprise Reporting**: Interactive audit dashboards, structured compliance summaries, and exportable reports.

---

## 🏗 Architecture

FlowShield operates as a **5-service containerized platform** orchestrated via Docker Compose:

```
                               ┌─────────────────────────────────────────┐
                               │        Next.js 14 Web Dashboard         │
                               │          (Port 3000 / React)            │
                               └────────────────────┬────────────────────┘
                                                    │ REST API
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │           FastAPI Backend Core          │
                               │        (Port 8000 / SQLModel)           │
                               └───┬─────────────────────────────────┬───┘
                                   │                                 │
                   PostgreSQL 15   │                    Task Queue   │
                   (Port 5432)     ▼                                 ▼
                     ┌──────────────────┐               ┌───────────────────────────┐
                     │ Database Engine  │               │     Async Scan Worker     │
                     │  (State & Auth)  │               │   (HTTPX + 16 Engines)    │
                     └──────────────────┘               └─────────────┬─────────────┘
                                                                      │
                                                ┌─────────────────────┴─────────────────────┐
                                                │                                           │
                                                ▼                                           ▼
                                 ┌─────────────────────────────┐             ┌─────────────────────────────┐
                                 │   AI Planner (Sandboxed)    │             │       Target APIs           │
                                 │  Groq Cloud / Local Ollama  │             │  MiniSub (:9000) / Custom   │
                                 └─────────────────────────────┘             └─────────────────────────────┘
```

### Services Overview
1. **Frontend (`frontend/`)**: Modern responsive UI built with Next.js 14 App Router, Tailwind CSS, real-time scan monitors, and findings triage.
2. **Backend (`backend/`)**: FastAPI management API handling project configuration, OpenAPI parsing, role definitions, and report generation.
3. **Scan Worker (`worker/`)**: High-performance HTTPX-based async fuzzing engine executing attack generation, verification loops, and AI planning.
4. **Database (`db`)**: PostgreSQL 15 persistent store managed with Alembic schema migrations.
5. **Vulnerable SaaS Target (`vulnerable-saas/`)**: "MiniSub", a realistic subscription management API with seeded vulnerabilities for validation.

---

## 🛡️ Detection Engines

FlowShield combines deterministic heuristics with AI planning across 16 specialized engines:

| Category | Engine | Target OWASP Risk | Description |
| :--- | :--- | :--- | :--- |
| **Authorization** | `BOLA Engine` | API1:2023 | Substitutes object IDs across tenants to detect cross-account data leaks. |
| **Authorization** | `BFLA Engine` | API5:2023 | Executes administrative endpoints using low-privileged role sessions. |
| **Data Integrity** | `Mass Assignment` | API3:2023 | Injects privileged attributes (`is_admin`, `role`, `verified`) into request bodies. |
| **Logic Flaws** | `SSPP (Path)` | Logic | Pollutes path parameters with nested segments and encoding overrides. |
| **Logic Flaws** | `SSPP (Query)` | Logic | Tests duplicate/array query parameters to bypass middleware validation. |
| **Logic Flaws** | `SSPP (Structured)`| Logic | Manipulates structured JSON payloads to alter state or permissions. |
| **Reconnaissance** | `Undocumented Routes` | API9:2023 | Probes for shadow/unlisted endpoints using curated wordlists. |
| **Reconnaissance** | `Hidden Parameters` | API9:2023 | Discovers hidden debugging flags (`debug=true`, `admin=1`, `test=1`). |
| **Reconnaissance** | `Method Discovery` | Method Tampering | Probes alternate HTTP verbs (`PUT`, `PATCH`, `DELETE`) on read endpoints. |
| **Reconnaissance** | `Content-Type Probe` | Parser Confusion | Fuzzes `Content-Type` headers (`application/xml`, `multipart/form-data`). |
| **Intelligence** | `AI Planner` | Test Generation | Generates contextual, schema-aware test payloads via Groq or Ollama. |
| **Analysis** | `Differential Analyzer`| Zero FP | Compares response status, length, and body deltas against baseline states. |
| **Validation** | `Verification Engine` | Evidence | Re-executes positive hits with control requests to guarantee zero false positives. |

---

## 🚀 Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose (v2.20+)
- (Optional) Groq API Key or local [Ollama](https://ollama.com/) instance

### 1. Clone the Repository
```bash
git clone https://github.com/yahya-elouarrak/Flow-Shield.git
cd Flow-Shield
```

### 2. Configure Environment
Copy the example environment configuration:
```bash
cp .env.example .env
```
*(Optionally add your `GROQ_API_KEY` in `.env` for ultra-fast AI test planning)*

### 3. Start the Platform
```bash
docker compose up --build -d
```

### 4. Access the Services
| Service | URL | Default Credentials |
| :--- | :--- | :--- |
| **FlowShield Dashboard** | [http://localhost:3000](http://localhost:3000) | No auth required (Dev Mode) |
| **Backend REST API** | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger Interactive Docs |
| **MiniSub Target API** | [http://localhost:9000/docs](http://localhost:9000/docs) | Seeded Vulnerable Playground |

---

## 🎮 Demo Walkthrough

FlowShield ships with **MiniSub SaaS** ready for end-to-end testing:

### 1. Create a Project
- Navigate to [http://localhost:3000/projects/new](http://localhost:3000/projects/new).
- Name: `MiniSub SaaS`
- Target API: `http://localhost:9000` *(FlowShield automatically maps `localhost:9000` to the internal Docker container)*

### 2. Import OpenAPI Specification
- In the project view, select **Import URL**.
- URL: `http://localhost:9000/openapi.json`
- FlowShield parses endpoints, parameters, and authentication requirements automatically.

### 3. Configure Multi-Role Accounts
Navigate to **Settings > Roles** and **Test Accounts** to set up test credentials:
- **Role `customer` (Level 10)**:
  - Account A: `customer_a@example.com` / `Password123`
  - Account B: `customer_b@example.com` / `Password123`
- **Role `support` (Level 50)**:
  - Account: `support@example.com` / `Password123`
- **Role `admin` (Level 100)**:
  - Account: `admin@example.com` / `Password123`

### 4. Configure Authentication Flow
Under **Target & Auth Settings**, configure JWT automated token generation:
- **Login Endpoint**: `/auth/login`
- **Username Field**: `email`
- **Password Field**: `password`
- **Token JSON Path**: `access_token`
- **Header Template**: `Authorization: Bearer {token}`

### 5. Launch Scan & Review Findings
- Navigate to **Scans > New Scan**.
- Select target engines (e.g., BOLA, BFLA, Mass Assignment, SSPP).
- Watch real-time execution: **Planning ➔ Executing ➔ Verifying ➔ Reporting**.
- Inspect confirmed findings with full request/response evidence and remediation advice.

For a full demo script and ground truth comparisons, see [docs/demo.md](docs/demo.md).

---

## 🤖 AI Planner Configuration

FlowShield supports both **Cloud High-Speed** and **Local Offline** LLM providers:

### Option A: Groq Cloud (Recommended for Speed)
Groq provides sub-second inference using Llama models:
1. In your `.env`:
   ```env
   LLM_PROVIDER=groq
   LLM_BASE_URL=https://api.groq.com/openai/v1
   LLM_MODEL=llama-3.1-8b-instant
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Option B: Ollama (100% Local & Air-Gapped)
1. Install [Ollama](https://ollama.com/) and pull the model:
   ```bash
   ollama pull qwen2.5-coder:7b
   ```
2. In your `.env`:
   ```env
   LLM_PROVIDER=ollama
   LLM_BASE_URL=http://host.docker.internal:11434
   LLM_MODEL=qwen2.5-coder:7b
   ```

> **Privacy Guarantee**: FlowShield sanitizes all prompts. Only HTTP methods, route patterns, and schema field names are shared with the LLM. Passwords, session tokens, and database records are **never** passed to the AI.

---

## 📁 Repository Structure

```
FlowShield/
├── backend/            # FastAPI core service
│   ├── app/api/        # REST routes (auth, projects, scans, findings, reports)
│   ├── app/models/     # SQLModel database entities
│   ├── app/services/   # OpenAPI parser & auth session manager
│   ├── alembic/        # Database schema migrations
│   └── requirements.txt
├── frontend/           # Next.js 14 dashboard UI
│   ├── src/app/        # App Router pages (dashboard, projects, scans, reports)
│   ├── src/components/ # Reusable UI components & layouts
│   └── src/lib/        # API client & TypeScript definitions
├── worker/             # Async security testing worker
│   ├── app/engines/    # 16 vulnerability detection & verification engines
│   ├── app/http/       # Async HTTP client with safety redactions
│   └── app/main.py     # Worker event loop & task coordinator
├── vulnerable-saas/    # MiniSub seeded vulnerable SaaS target
│   └── app/routes/     # Vulnerable endpoints (invoices, subscriptions, admin)
├── wordlists/          # Curated lists for parameter & route discovery
├── docs/               # Benchmarks, demo guides, and research audits
├── examples/           # Sample OpenAPI specifications
└── docker-compose.yml  # Multi-container local orchestration
```

---

## 🛠 Troubleshooting

- **Containers cannot reach `localhost:9000`**: FlowShield automatically rewrites `localhost:9000` to `vulnerable-saas:9000` when executing inside Docker.
- **Database Schema Reset**:
  ```bash
  docker compose down -v
  docker compose up --build -d
  ```
- **Worker AI Fallback**: If Groq or Ollama is unreachable, FlowShield automatically falls back to deterministic heuristic scanning without interrupting the test execution.

---

