# PolicyForge Constitution

## Project Overview
PolicyForge is an AI-native enterprise security policy platform for Track 1 (Agent Security & AI Governance) of the TechEx Intelligent Enterprise Solutions Hackathon. It allows security teams to write AI agent security policies in plain English, which Gemini converts to Lobster Trap YAML rules that enforce automatically.

## Core Principles

### I. Security-First (NON-NEGOTIABLE)
All policy enforcement runs through Veea Lobster Trap as the trust layer. No agent traffic bypasses the proxy. Every action is logged and auditable. Policy rules follow least-privilege by default.

### II. Natural Language as the Interface
Security teams write policies in plain English. Gemini translates to Lobster Trap YAML. No manual YAML editing required. The generated YAML is always shown for transparency before activation.

### III. Measurable Security Outcomes
Every policy shows: blocked_count, allowed_count, risk_score. Dashboards display real-time attack detection. Export-ready audit reports for HIPAA, SOC2, PCI-DSS compliance.

### IV. Hackathon Scope (STRICT)
Only build what is needed for a winning demo. No auth system, no multi-tenancy, no production infrastructure. Focus: policy creation flow + enforcement demo + compliance report export. Simplest viable implementation wins.

### V. Test-First for Core Logic
Policy generation (NL → YAML) must have unit tests. Lobster Trap integration tested with mock agents. UI tested for the golden path: create policy → see it enforced → export report.

### VI. Fast Stack (5-day delivery)
- Frontend: Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn/ui
- Backend: Python + FastAPI (uv, never pip)
- AI: Google Gemini 2.0 Flash (free tier, fastest)
- Security Proxy: Veea Lobster Trap (Docker container)
- Storage: SQLite (policies + audit logs, zero infra)
- Deploy: Railway (backend) + Vercel (frontend)

## Technical Constraints

### Lobster Trap Integration
- Run Lobster Trap as Docker container on port 8080
- All test agent calls routed through Lobster Trap proxy
- Policy YAML written to `configs/policies/` directory
- Use `./lobstertrap inspect` for single-prompt debugging

### Gemini Usage
- Model: `gemini-2.0-flash-exp` (free, fast)
- System prompt: strict YAML-only output for policy generation
- Temperature: 0.1 for deterministic policy generation
- Always validate generated YAML before saving

### API Design
- `POST /api/policies/generate` — NL → YAML (Gemini)
- `POST /api/policies/activate` — write YAML to Lobster Trap config
- `GET /api/policies` — list all policies
- `GET /api/audit/logs` — recent blocked/allowed events
- `GET /api/audit/report` — compliance report (HIPAA/SOC2/PCI-DSS)
- `POST /api/demo/attack` — fire test attack through proxy

## Development Workflow
1. Backend (FastAPI) first — policy generation + Lobster Trap integration
2. Frontend (Next.js) second — policy editor + dashboard
3. Demo flow last — attack simulation + audit report
4. PHR after every prompt, no exceptions

## Governance
Constitution supersedes all implementation decisions. Amendments require explicit user approval. Complexity must be justified against 5-day hackathon constraint.

**Version**: 1.0.0 | **Ratified**: 2026-05-14 | **Last Amended**: 2026-05-14
