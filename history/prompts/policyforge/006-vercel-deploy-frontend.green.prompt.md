---
id: "006"
title: Deploy frontend to Vercel
stage: green
date: 2026-05-15
surface: agent
model: claude-sonnet-4-6
feature: policyforge
branch: main
user: Muhammad Yaseen
command: continue
labels: ["vercel", "deploy", "frontend", "nextjs", "env-var"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/vercel.json
tests:
  - GET https://policyforge-eight.vercel.app/ → page title "PolicyForge — AI Agent Security"
---

## Prompt

Continue (continue from prior context: deploy frontend to Vercel)

## Response snapshot

1. Simplified `frontend/vercel.json` — removed `@policyforge_api_url` secret reference (not set in Vercel), left framework/build settings only.
2. Committed PHR 005 + vercel.json change, pushed to `my5757980/policyforge` main.
3. Opened Vercel → New Project → imported `my5757980/policyforge`.
4. Set Root Directory = `frontend` (Next.js auto-detected).
5. Expanded Environment Variables → added `NEXT_PUBLIC_API_URL=https://policyforge-production-1fe6.up.railway.app`.
6. Clicked Deploy → build completed successfully.

## Outcome

- ✅ Impact: Frontend live at https://policyforge-eight.vercel.app — title "PolicyForge — AI Agent Security", all nav links present (Dashboard, Policy Editor, Attack Demo, Compliance Report)
- 🧪 Tests: Browser navigation confirmed page loads with correct content
- 📁 Files: frontend/vercel.json (simplified)
- 🔁 Next prompts: Record 2-3 min demo video, submit on lablab.ai by May 19
- 🧠 Reflection: Secret references (@var) in vercel.json require pre-created Vercel secrets — for hackathons, omit and set env vars directly in the import UI

## Evaluation notes (flywheel)

- Failure modes observed: Page navigated away on first attempt (root dir modal click triggered navigation); resolved by reloading import URL
- Graders run and results (PASS/FAIL): Manual browser check PASS
- Prompt variant (if applicable): n/a
- Next experiment: n/a
