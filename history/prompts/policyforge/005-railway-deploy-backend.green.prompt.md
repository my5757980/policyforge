---
name: 005-railway-deploy-backend
description: Backend deployed to Railway with public URL live - fixed PORT expansion, Neon DB, domain generated
metadata:
  type: green
  stage: green
  date: 2026-05-15
  surface: agent
  model: claude-sonnet-4-6
  feature: policyforge
  branch: main
  user: Muhammad Yaseen
  labels: ["railway", "deploy", "backend", "port-fix", "neon-postgres"]
---

## Summary

Backend successfully deployed to Railway. Public URL live: https://policyforge-production-1fe6.up.railway.app

## Key Fixes Applied

1. **PORT expansion bug**: Railway start command used `$PORT` literal — fixed by wrapping with `sh -c` in railway.json
2. **Explicit PORT=8080**: Added PORT=8080 as a Railway variable to ensure it's always set
3. **Domain generated**: policyforge-production-1fe6.up.railway.app on port 8080
4. **Healthcheck removed**: railway.json has no healthcheck (avoids Network→Healthcheck failures)
5. **Neon PostgreSQL**: DATABASE_URL set without channel_binding (psycopg2 doesn't support it)

## Files Changed

- `backend/railway.json` — startCommand changed to `sh -c 'uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}'`

## Railway Variables Set

- GEMINI_API_KEY
- DATABASE_URL (Neon PostgreSQL, sslmode=require)
- MOCK_LOBSTERTRAP=true
- LOBSTERTRAP_URL=http://localhost:8080
- CORS_ORIGINS=*
- PORT=8080

## Verification

`GET https://policyforge-production-1fe6.up.railway.app/health` → `{"status":"ok","service":"PolicyForge API"}`

## Next Steps

- Deploy frontend to Vercel with NEXT_PUBLIC_API_URL=https://policyforge-production-1fe6.up.railway.app
- Record 2-3 min demo video
- Submit on lablab.ai by May 19
