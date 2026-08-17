# PolicyForge — AI Agent Security Policy Platform

> **TechEx Intelligent Enterprise Solutions Hackathon 2026**
> Track 1: Agent Security & AI Governance | Prize Pool: $10,000

PolicyForge lets enterprise security teams write AI agent security policies in plain English. Gemini 2.0 Flash converts them to Lobster Trap YAML enforcement rules — no YAML knowledge needed.

---

## Demo Flow (2 minutes)

1. **Policy Editor** → Type: *"Block any agent that tries to read patient SSN or medical records"*
2. **Generate** → Gemini creates a Lobster Trap YAML rule in ~2 seconds
3. **Activate** → Policy enforced immediately
4. **Attack Demo** → Fire "PII Exfiltration" attack → See `BLOCK` with 95% risk score
5. **Dashboard** → Blocked count increments, audit trail updates live
6. **Compliance Report** → Generate HIPAA report → Download .md

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
└──────────────┬──────────────────────┘
               │ Policy YAML + Proxy
┌──────────────▼──────────────────────┐
│   Veea Lobster Trap (Port 8080)     │
│   Deep Prompt Inspection Proxy      │
│   YAML Policy Enforcement           │
└─────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind CSS |
| Backend | Python + FastAPI, uv |
| AI | Google Gemini 2.0 Flash |
| Security | Veea Lobster Trap (MIT) |
| Database | SQLite via SQLModel |
| Deploy | Vercel (frontend) + Railway (backend) |

---

## Local Setup

### Prerequisites
- Python 3.11+ with [uv](https://docs.astral.sh/uv/)
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

### Lobster Trap (Optional — Mock mode enabled by default)

```bash
cd lobstertrap
docker compose up
```

Set `MOCK_LOBSTERTRAP=false` in `backend/.env` to use real enforcement.

---

## Environment Variables

```env
GEMINI_API_KEY=your_key_here
LOBSTERTRAP_URL=http://localhost:8080
MOCK_LOBSTERTRAP=true          # false = real Lobster Trap enforcement
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
| `GET` | `/api/audit/report?standard=HIPAA` | Compliance report |
| `GET` | `/api/demo/attacks` | Available attack types |
| `POST` | `/api/demo/attack` | Fire a test attack |

---

## Hackathon Info

- **Event**: [TechEx Intelligent Enterprise Solutions Hackathon](https://lablab.ai/ai-hackathons/techex-intelligent-enterprise-solutions-hackathon)
- **Track**: Track 1 — Agent Security & AI Governance
- **Powered by**: Veea Lobster Trap + Google Gemini
- **Team**: Muhammad Yaseen
- **Deadline**: May 19, 2026
