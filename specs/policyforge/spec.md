# PolicyForge — Feature Specification

## Metadata
- **Feature**: policyforge
- **Track**: Track 1 — Agent Security & AI Governance (TechEx Hackathon)
- **Deadline**: May 19, 2026, 5:00 AM PKT
- **Version**: 1.0.0
- **Status**: Draft

---

## 1. Problem Statement

Enterprise security teams cannot easily secure AI agents. Writing Lobster Trap YAML security policies requires deep technical knowledge. A single misconfigured or missing policy can allow prompt injection, credential exfiltration, or unauthorized agent actions in production systems.

**Core pain**: Security teams speak English, not YAML. The gap between intent and enforcement is dangerous.

---

## 2. Solution

PolicyForge bridges this gap:

1. **Write** — Security team describes a policy in plain English (e.g., "Block any agent that tries to read credit card numbers")
2. **Generate** — Gemini 2.0 Flash converts it to a valid Lobster Trap YAML rule
3. **Review** — User sees the generated YAML, can edit or approve
4. **Activate** — Policy is written to Lobster Trap config and enforced immediately
5. **Monitor** — Real-time dashboard shows blocked attacks, risk scores, audit trail
6. **Export** — One-click compliance report (HIPAA / SOC2 / PCI-DSS)

---

## 3. User Stories

### US-001: Policy Creation
**As a** security engineer  
**I want to** describe a security policy in plain English  
**So that** I don't need to manually write YAML rules

**Acceptance Criteria:**
- [ ] Input field accepts multi-line natural language description
- [ ] "Generate Policy" button calls Gemini API
- [ ] Generated YAML displays with syntax highlighting
- [ ] User can edit generated YAML before saving
- [ ] "Activate Policy" saves to Lobster Trap config and reloads proxy
- [ ] Policy appears in policy list with name, status, created date

### US-002: Attack Simulation Demo
**As a** security engineer  
**I want to** test my policies against real attack patterns  
**So that** I can verify enforcement before production deployment

**Acceptance Criteria:**
- [ ] Demo panel shows list of attack types (prompt injection, PII exfiltration, jailbreak, credential theft)
- [ ] "Fire Attack" sends malicious prompt through Lobster Trap proxy
- [ ] Result shows: BLOCKED / ALLOWED + which policy triggered
- [ ] Lobster Trap audit log updates in real-time
- [ ] Dashboard counter increments for blocked_count

### US-003: Real-time Security Dashboard
**As a** security manager  
**I want to** see live metrics on agent security activity  
**So that** I can monitor risk posture at a glance

**Acceptance Criteria:**
- [ ] Dashboard shows: total_policies, active_policies, blocked_today, allowed_today, risk_score
- [ ] Last 20 audit log entries displayed with timestamp, action (BLOCK/ALLOW), matched_rule, intent_category
- [ ] Auto-refreshes every 5 seconds
- [ ] Color-coded risk score (green/yellow/red)

### US-004: Compliance Report Export
**As a** compliance officer  
**I want to** generate a compliance audit report  
**So that** I can demonstrate AI governance to regulators

**Acceptance Criteria:**
- [ ] Select compliance standard: HIPAA, SOC2, or PCI-DSS
- [ ] Report generates as PDF/Markdown showing: active policies, blocked events, PII protection status, audit trail summary
- [ ] Report includes timestamp and policy version
- [ ] Download button exports the report

---

## 4. Technical Architecture

### 4.1 System Components

```
┌──────────────────────────────────────────────────────────┐
│                    PolicyForge UI                         │
│              Next.js 15 (Port 3000)                       │
│   [Policy Editor] [Dashboard] [Demo Panel] [Reports]     │
└─────────────────────┬────────────────────────────────────┘
                      │ REST API calls
┌─────────────────────▼────────────────────────────────────┐
│                  PolicyForge API                          │
│                FastAPI (Port 8000)                        │
│   /policies  /audit  /demo  /report                      │
│                    │                │                     │
│             Gemini API        SQLite DB                   │
│           (policy gen)     (policies+logs)                │
└─────────────────────┬────────────────────────────────────┘
                      │ Policy YAML write + Proxy
┌─────────────────────▼────────────────────────────────────┐
│              Veea Lobster Trap                            │
│                 (Port 8080)                               │
│   Deep Prompt Inspection Proxy                           │
│   YAML Policy Enforcement                               │
│   Audit Logs + Risk Scoring                             │
└─────────────────────┬────────────────────────────────────┘
                      │ Forward (OpenAI-compatible)
                 LLM Backend (Gemini via proxy)
```

### 4.2 Data Models

**Policy**
```python
id: str (uuid)
name: str
description: str           # original natural language input
yaml_content: str          # generated Lobster Trap YAML
is_active: bool
compliance_tags: list[str] # ["HIPAA", "SOC2", "PCI-DSS"]
created_at: datetime
```

**AuditLog**
```python
id: int (autoincrement)
timestamp: datetime
action: str                # "BLOCK" | "ALLOW" | "LOG"
intent_category: str       # from Lobster Trap metadata
risk_score: float          # 0.0 - 1.0
matched_rule: str          # policy name that triggered
prompt_excerpt: str        # first 100 chars (sanitized)
```

### 4.3 Gemini Policy Generation Prompt

```
System: You are a Lobster Trap YAML security policy generator.
Generate ONLY valid YAML following the Lobster Trap policy schema.
Output nothing except the YAML block.

Schema:
rules:
  - name: <rule-name>
    match:
      intent: [list of intents to match]
      pii: [ssn, credit_card, api_key, password] (optional)
      keywords: [list] (optional)
    action: DENY | LOG | HUMAN_REVIEW | QUARANTINE
    log: true
    message: <denial message>

User: {natural_language_description}
```

---

## 5. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Policy generation latency | < 3 seconds (Gemini Flash) |
| Dashboard refresh rate | 5 seconds |
| Audit log retention | In-memory + SQLite (hackathon scope) |
| Lobster Trap startup | < 10 seconds (Docker) |
| Demo attack response | < 1 second |

---

## 6. Out of Scope (Hackathon)

- User authentication / multi-tenancy
- Production Kubernetes deployment
- Real LLM backend (Gemini proxy via Lobster Trap uses mock responses for demo)
- Policy versioning / rollback
- Webhook notifications
- Team collaboration features

---

## 7. Acceptance Criteria (Definition of Done)

- [ ] User can create a policy from plain English in < 30 seconds
- [ ] Policy is enforced via Lobster Trap (verifiable via attack simulation)
- [ ] Dashboard shows real-time blocked attack count
- [ ] Compliance report exports with at least HIPAA standard
- [ ] Working demo: create policy → fire attack → see it blocked → export report
- [ ] Public GitHub repo with README
- [ ] 2-3 minute demo video recorded
- [ ] Deployed: frontend on Vercel, backend on Railway

---

## 8. Risks

1. **Lobster Trap Docker on Windows** — may need WSL2; mitigation: use pre-built binary alternative
2. **Gemini YAML reliability** — LLM may generate invalid YAML; mitigation: validate + retry with correction prompt
3. **Demo timing** — 5 days tight; mitigation: mock Lobster Trap responses if Docker fails, focus on UI demo quality
