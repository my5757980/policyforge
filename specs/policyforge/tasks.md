# PolicyForge — Tasks

## Metadata
- **Feature**: policyforge
- **Version**: 1.0.0
- **Date**: 2026-05-14

---

## Phase 1: Foundation

### TASK-001: Project Structure + Git Init
- [ ] Create `backend/` with `uv init`
- [ ] Create `frontend/` with `npx create-next-app@latest`
- [ ] Create `lobstertrap/` config directory
- [ ] Add `.gitignore`, `README.md` skeleton
- [ ] `git init` and initial commit

### TASK-002: Lobster Trap Setup
- [ ] Create `lobstertrap/docker-compose.yml` to run LT container
- [ ] Create `lobstertrap/config.yaml` with base policy (LOG all)
- [ ] Create `lobstertrap/default_policy.yaml` with default DENY rules
- [ ] Test LT starts and responds on port 8080
- [ ] Add `MOCK_LOBSTERTRAP=true` fallback mode to backend

### TASK-003: Backend — FastAPI Skeleton
- [ ] `pyproject.toml` with deps: fastapi, uvicorn, sqlmodel, google-generativeai, pyyaml, python-dotenv
- [ ] `app/main.py` — FastAPI app + CORS + router includes
- [ ] `app/db.py` — SQLite engine + create_tables()
- [ ] `app/models/policy.py` — Policy SQLModel
- [ ] `app/models/audit_log.py` — AuditLog SQLModel
- [ ] `GET /health` endpoint returns `{"status": "ok"}`
- [ ] `.env.example` with GEMINI_API_KEY, LOBSTERTRAP_URL, MOCK_LOBSTERTRAP

---

## Phase 2: Policy Generation Engine

### TASK-004: Gemini Policy Generation Service
- [ ] `app/services/gemini_service.py`
- [ ] `generate_policy_yaml(description: str) -> str` function
- [ ] System prompt for strict YAML-only output
- [ ] YAML validation (pyyaml.safe_load)
- [ ] Retry once with correction prompt if invalid YAML
- [ ] Unit test: test_generate_policy.py (3 test cases)

### TASK-005: Lobster Trap Service
- [ ] `app/services/lobster_service.py`
- [ ] `write_policy_yaml(policy_id, yaml_content)` — write to configs/policies/
- [ ] `reload_lobstertrap()` — restart Docker container via shell
- [ ] `get_audit_logs(limit)` — read LT logs from file or mock
- [ ] `get_metrics()` — return blocked, allowed, risk_score
- [ ] Mock mode: return simulated data when MOCK_LOBSTERTRAP=true

### TASK-006: Policy CRUD Endpoints
- [ ] `POST /api/policies/generate` — calls Gemini, returns yaml + suggested name
- [ ] `POST /api/policies/activate` — saves to DB + writes YAML + reloads LT
- [ ] `GET /api/policies` — list all policies
- [ ] `DELETE /api/policies/{id}` — deactivate + remove YAML file
- [ ] `GET /api/audit/logs` — last N audit entries from DB
- [ ] `GET /api/metrics` — dashboard metrics

---

## Phase 3: Frontend

### TASK-007: Next.js Setup + Layout
- [ ] Install deps: shadcn/ui init, @uiw/react-codemirror, tailwind
- [ ] `app/layout.tsx` — dark theme, sidebar navigation
- [ ] Sidebar: Dashboard | Policy Editor | Attack Demo | Reports
- [ ] API client: `lib/api.ts` with all endpoint calls
- [ ] Types: `lib/types.ts` for Policy, AuditLog, Metrics

### TASK-008: Dashboard Page (`/`)
- [ ] MetricsBar component: 4 stat cards (total, active, blocked_today, risk_score)
- [ ] Risk score color: green < 0.3, yellow < 0.7, red >= 0.7
- [ ] AuditFeed component: table with timestamp, action badge, rule, intent
- [ ] Auto-refresh every 5 seconds using setInterval
- [ ] Loading skeletons while data fetches

### TASK-009: Policy Editor Page (`/policies`)
- [ ] Natural language textarea (left panel)
- [ ] Compliance tag checkboxes: HIPAA, SOC2, PCI-DSS
- [ ] "Generate Policy" button + loading state (spinner)
- [ ] YamlViewer: react-codemirror with YAML syntax highlighting (right panel)
- [ ] "Activate Policy" button → calls activate endpoint → shows success toast
- [ ] Policy list table: name, status (active/inactive), created_at, compliance tags
- [ ] Error handling: show error if Gemini fails

### TASK-010: Attack Demo Page (`/demo`)
- [ ] Attack type selector: 5 predefined attacks (cards with description)
- [ ] "Fire Attack" button → POST to /api/demo/attack
- [ ] Result display: BLOCKED (red badge) / ALLOWED (green badge)
- [ ] Show: matched_rule, intent_category, risk_score, response_time
- [ ] Attack history table: last 10 attacks fired in this session
- [ ] Confetti/animation when attack is blocked (fun for demo)

### TASK-011: Compliance Report Page (`/report`)
- [ ] Standard selector: HIPAA | SOC2 | PCI-DSS (tab or radio)
- [ ] "Generate Report" button → GET /api/audit/report
- [ ] Report preview: executive summary, policy list, audit trail, checklist
- [ ] "Download Report" → downloads as .md file
- [ ] Report shows PolicyForge branding + timestamp

---

## Phase 4: Demo + Report API

### TASK-012: Demo Attack Endpoint
- [ ] `POST /api/demo/attack` body: `{ attack_type: str }`
- [ ] Pre-configured attack prompts per type
- [ ] Send prompt through Lobster Trap proxy
- [ ] Return: action (BLOCK/ALLOW), matched_rule, risk_score, latency_ms
- [ ] Save to AuditLog DB
- [ ] Mock mode returns realistic fake response

### TASK-013: Compliance Report Endpoint
- [ ] `GET /api/audit/report?standard=HIPAA`
- [ ] Build ComplianceReport object from DB data
- [ ] HIPAA checklist: 5 items mapped to active policies
- [ ] SOC2 checklist: CC6.1, CC6.2, CC6.3, CC6.6, CC6.7
- [ ] PCI-DSS checklist: 6.4, 6.5, 8.2, 10.2
- [ ] Return as JSON (frontend renders as Markdown)

---

## Phase 5: Deploy + Polish

### TASK-014: Docker + Deploy Config
- [ ] `backend/Dockerfile` — multi-stage FastAPI build
- [ ] `railway.json` — Railway deploy config
- [ ] `vercel.json` — Vercel deploy config
- [ ] Environment variables documented in README

### TASK-015: README + Demo Script
- [ ] Architecture diagram (ASCII)
- [ ] Setup instructions (local + Docker)
- [ ] Demo video link placeholder
- [ ] Hackathon submission info (track, tech used)
- [ ] Screenshots section

### TASK-016: Demo Polish
- [ ] Test full golden path: create policy → activate → fire attack → blocked → export report
- [ ] Verify mobile responsiveness (judges may use phone)
- [ ] Check all error states show graceful messages
- [ ] Record 2-3 minute demo video
- [ ] Submit on lablab.ai

---

## Dependency Order
```
001 → 002 → 003 → 004 → 005 → 006 → 007 → 008 → 009 → 010 → 011 → 012 → 013 → 014 → 015 → 016
```

All tasks are sequential. Backend must be complete before frontend API calls work.
