# PolicyForge — AI Agent Security Policy Platform

> **TechEx Intelligent Enterprise Solutions Hackathon 2026**
> Track 1: Agent Security & AI Governance | Prize Pool: $10,000

PolicyForge lets enterprise security teams write AI agent security policies in plain English. Gemini 2.0 Flash turns them into YAML policy rules — no YAML knowledge needed — and every test attack is checked against the policies you have active.

---

## Demo Flow (2 minutes)

1. **Policy Editor** → Type: *"Block any agent that tries to read patient SSN or medical records"*
2. **Generate** → Gemini writes a PolicyForge YAML rule (keywords, PII types, intents) in ~2 seconds
3. **Activate** → The policy joins the set every attack is checked against
4. **Attack Demo** → Fire "PII Exfiltration" → see what your policies really do: `BLOCK` with the rule and the words that matched, or `ALLOW` when no active rule covers it
5. **Dashboard** → Blocked and allowed counts and the audit trail come from those checks
6. **Compliance Report** → Generate HIPAA report → Download .md

## How attacks are checked

Each attack prompt is checked against every **active** policy, rule by rule, and the first rule that
matches decides (`DENY` → `BLOCK`, `LOG` → `LOG`). A rule matches when one of its `keywords` appears
in the prompt as a whole word or phrase, or one of its `pii` types is named or present (for example
"SSN" or `123-45-6789`). The result names the policy, the rule and exactly what matched.

What it does not do: a rule's `intent` list is not evaluated, because that needs an intent classifier.
A rule with only `intent` therefore never matches and is reported as unchecked. No risk score is
produced, so none is shown.

PolicyForge's policy YAML is its own schema. It is not the policy format of Veea Lobster Trap, and
there is no Lobster Trap proxy in this project.

## What the compliance report shows

The HIPAA, SOC2 and PCI-DSS checklists are evidence from PolicyForge's own policies and audit log, not
a certification. Each item states what it was checked against (for example "at least one attack was
blocked"). Items that data cannot show, such as SOC2 CC6.3 and PCI Req 8.2 (PolicyForge has no user
accounts), are marked **not assessed** instead of ticked. The totals count every audit event.

---

## Architecture

```
┌─────────────────────────────────────┐
│   PolicyForge UI (Next.js 15)       │
│   Dashboard | Editor | Demo | Report│
└──────────────┬──────────────────────┘
               │ REST API
┌──────────────▼──────────────────────┐
│   PolicyForge API (FastAPI)         │
│   Gemini 2.0 Flash | SQLite         │
│   Policy check: keywords + PII      │
└─────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind CSS |
| Backend | Python + FastAPI, uv |
| AI | Google Gemini 2.0 Flash |
| Policy check | PolicyForge's own keyword + PII matcher (`backend/app/services/policy_check.py`) |
| Database | SQLite via SQLModel |
| Deploy | Vercel (frontend) + Railway (backend) |

---

## Local Setup

### Prerequisites
- Python 3.13+ with [uv](https://docs.astral.sh/uv/)
- Node.js 18+
- Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### Backend

```bash
cd backend
cp .env.example .env
# Add your GEMINI_API_KEY to .env
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Tests

```bash
cd backend
uv run pytest
```

---

## Environment Variables

```env
GEMINI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./policyforge.db
CORS_ORIGINS=http://localhost:3000
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/policies/generate` | NL → YAML via Gemini |
| `POST` | `/api/policies/save` | Save + activate policy |
| `GET` | `/api/policies` | List all policies |
| `DELETE` | `/api/policies/{id}` | Deactivate policy |
| `GET` | `/api/audit/logs` | Recent audit events |
| `GET` | `/api/audit/metrics` | Dashboard metrics |
| `GET` | `/api/audit/report?standard=HIPAA` | Compliance report (`HIPAA`, `SOC2` or `PCI-DSS`; others get 400) |
| `GET` | `/api/demo/attacks` | Available attack types |
| `POST` | `/api/demo/attack` | Check a test attack against the active policies |

---

## Hackathon Info

- **Event**: [TechEx Intelligent Enterprise Solutions Hackathon](https://lablab.ai/ai-hackathons/techex-intelligent-enterprise-solutions-hackathon)
- **Track**: Track 1 — Agent Security & AI Governance
- **Powered by**: Google Gemini (Veea Lobster Trap is not integrated; see [How attacks are checked](#how-attacks-are-checked))
- **Team**: Muhammad Yaseen
- **Deadline**: May 19, 2026
