# Claude Code Session Instructions

> **READ THIS FIRST** - Always check this file at the start of every session.

---

## Current Status

| Item | Status |
|------|--------|
| **UI** | ✅ COMPLETE (v3.0) |
| **Backend Code** | ✅ Phase 1 COMPLETE |
| **Upstash Redis** | ✅ Connected & tested |
| **Upstash Vector** | ✅ Hybrid index ready |
| **Groq API** | ✅ Llama 3.3 70B (~395ms) |
| **Supabase PostgreSQL** | ⏳ DNS issue - needs troubleshooting |
| **Deployment** | Local Flask only |

---

## Priority Queue

### 🔴 IMMEDIATE: Finish Supabase PostgreSQL Setup

**Problem:** DNS resolution failing for `db.kuzcgmolzqvulwypvoun.supabase.co`

**Troubleshooting Steps:**
1. Check Supabase dashboard - is project status "Active"?
2. Try the **Pooler connection** (port 6543) instead of direct (port 5432)
3. In Supabase: Settings → Database → Connection Pooling → Copy "Transaction" mode URI
4. Check if on VPN/corporate network blocking port 5432
5. Try `ping db.kuzcgmolzqvulwypvoun.supabase.co` to test DNS

**Test command:**
```powershell
$env:DATABASE_URL='postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres'
python test_postgres.py
```

### ✅ COMPLETED: Phase 1 - Security Foundation

Files created in `roofio-backend/common/`:
- `config.py` - Environment configuration (all env vars)
- `session.py` - Redis-backed sessions (JWT, sliding expiration)
- `security.py` - RBAC (5 roles), OAuth (4 providers), circuit breakers, LLM fallback
- `database.py` - PostgreSQL async with multi-tenant scoping

### 🔜 AFTER DATABASE: Phase 2 - Tier 1 Python Layer
1. Create database tables using SQLAlchemy models
2. Implement user/agency CRUD in `tier1/`
3. Implement project CRUD
4. Wire up authentication to Flask frontend

### Future Phases
- Phase 3: Tier 2 Groq + RAG integration (brain/knowledge.py)
- Phase 4: Tier 3 Advanced LLM with failover
- Phase 5: Master Architect self-healing

---

## What's Done (Don't Redo)

### Backend Infrastructure (NEW - Dec 8, 2024)
- `roofio-backend/common/` - Complete security foundation
- Upstash Redis account - Sessions, rate limiting, audit
- Upstash Vector index - Hybrid (dense+sparse) for RAG
- Groq API - Llama 3.3 70B verified working
- Test scripts for all services (`test_*.py`)

### UI Pages (9 total)
- `/dashboard` - Company Dashboard with 6 seats
- `/analysis` - Document upload and analysis
- `/roofio` - AI chat with 14 skills
- `/control-center` - 8 positions with AI toggles
- `/digital-foreman` - Risk Shield field docs
- `/integrations` - 28+ service connectors
- `/projects` - Project management
- `/inspector/<id>` - Guest inspector access
- `/phone` - Phone integration placeholder

### Platform Architecture
- Database schema designed (`roofio/platform/database/schema.sql`)
- Digital Foreman schema (`roofio/platform/digital_foreman/schema.sql`)
- Risk Shield architecture documented
- Integration Hub spec complete
- UPO (User & Project Organization) designed

### Skills Documentation
- 14 SKILL.md files in `roofio/skills/`
- FM Global, NRCA, SPRI, IIBEC, ASCE 7
- Roofing systems, wind uplift, leak detection
- Division 07 testing and inspections

---

## Quick Commands

### Run the App
```bash
cd roofing_intelligence
python app.py
# http://127.0.0.1:5000
```

### Git Workflow
```bash
# Create feature branch
git checkout -b claude/feature-name-sessionId

# Commit and push
git add -A
git commit -m "Description"
git push -u origin claude/feature-name-sessionId
```

### Test All Pages Load
```bash
curl -s http://127.0.0.1:5000/dashboard | head -20
curl -s http://127.0.0.1:5000/analysis | head -20
curl -s http://127.0.0.1:5000/roofio | head -20
curl -s http://127.0.0.1:5000/control-center | head -20
curl -s http://127.0.0.1:5000/digital-foreman | head -20
curl -s http://127.0.0.1:5000/integrations | head -20
curl -s http://127.0.0.1:5000/projects | head -20
```

---

## Key Reference Files

| File | Purpose |
|------|---------|
| `README.md` | Full project documentation |
| `CLAUDE.md` | CAD Observer context (original project) |
| `NEXT-SESSION-BACKEND-MASTERPLAN.md` | Detailed backend implementation plan |
| `roofio/platform/ROOFIO-PLATFORM-SPEC-v2.md` | UPO architecture |
| `roofio/platform/INTEGRATION-HUB-SPEC.md` | Integration strategy |

---

## Environment Variables Needed (for Backend)

```powershell
# Upstash Redis (✅ CONFIGURED)
$env:UPSTASH_REDIS_REST_URL='https://discrete-swine-5337.upstash.io'
$env:UPSTASH_REDIS_REST_TOKEN='your-token'

# Upstash Vector (✅ CONFIGURED)
$env:UPSTASH_VECTOR_REST_URL='https://pure-phoenix-92332-us1-vector.upstash.io'
$env:UPSTASH_VECTOR_REST_TOKEN='your-token'

# Groq API (✅ CONFIGURED)
$env:GROQ_API_KEY='gsk_...'

# Supabase PostgreSQL (⏳ DNS ISSUE)
$env:DATABASE_URL='postgresql://postgres:PASSWORD@db.kuzcgmolzqvulwypvoun.supabase.co:5432/postgres'

# Security (generate these for production)
$env:JWT_SECRET='your-32-byte-secret'
$env:ENCRYPTION_KEY='your-fernet-key'

# Optional
$env:ANTHROPIC_API_KEY='sk-ant-...'
$env:OPENAI_API_KEY='sk-...'
```

**See `roofio-backend/.env.example` for full template.**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         APPIO UI                            │
│  Dashboard | Analysis | Roofio | Control | Foreman | Integ  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Backend (app.py)                   │
│              Routes, SSE, File Handling                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │  Tier 0   │  │  Tier 1   │  │  Tier 2   │
    │  Python   │  │   Groq    │  │  Claude   │
    │   FREE    │  │  $0.0006  │  │  $0.01    │
    │   95%     │  │    4%     │  │    1%     │
    └───────────┘  └───────────┘  └───────────┘
```

---

## Armand's Context

- 20+ year journeyman roofer/waterproofer
- Local 30 union member
- Projects: UMass waterproofing, JHU Library
- Uses AutoCAD LT for shop drawings
- Division 07 specs: 07 62 00, 07 50 00, 07 27 00, 07 92 00

---

## Session Handoff Template

When ending a session, update this section:

### Last Session Summary
**Date:** December 8, 2024
**Completed:**
- ✅ Backend Phase 1 - Security Foundation (all 4 files)
- ✅ Upstash Redis - Account created, tested, working
- ✅ Upstash Vector - Hybrid index (384 dim), tested, working
- ✅ Groq API - Key obtained, tested (~395ms response)
- ⏳ Supabase PostgreSQL - Account created, DNS resolution failing
- ✅ Test scripts for all services
- ✅ .env.example template
- ✅ Updated README and this file

**Next Session Should:**
1. **FIRST:** Troubleshoot Supabase DNS issue:
   - Check if project is fully provisioned (Active status)
   - Try Pooler connection (port 6543) instead of direct
   - Test: `ping db.kuzcgmolzqvulwypvoun.supabase.co`
   - Check VPN/firewall issues
2. Once DB works, run `python test_postgres.py`
3. Start Phase 2: Create SQLAlchemy models and user CRUD

---

## Contact

For questions about the project, check:
1. This file first
2. `README.md` for features/structure
3. `NEXT-SESSION-BACKEND-MASTERPLAN.md` for backend details
4. `CLAUDE.md` for CAD Observer context
