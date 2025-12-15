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
| **Supabase PostgreSQL** | ✅ Connected via pooler |
| **Deployment** | Local Flask only |

---

## Priority Queue

### ✅ COMPLETED: Supabase PostgreSQL Setup

**Status:** Connected via IPv4-compatible pooler connection (port 6543).

### ✅ COMPLETED: Phase 1 - Security Foundation

Files created in `roofio-backend/common/`:
- `config.py` - Environment configuration (all env vars)
- `session.py` - Redis-backed sessions (JWT, sliding expiration)
- `security.py` - RBAC (5 roles), OAuth (4 providers), circuit breakers, LLM fallback
- `database.py` - PostgreSQL async with multi-tenant scoping

### ✅ COMPLETED: Phase 2 - Database Tables
- SQLAlchemy models for all entities (Agency, User, Project, Form)
- Migration scripts for table creation
- CRUD operations in API routes

### ✅ COMPLETED: Phase 3 - REST API + Forms
- FastAPI application with all routes
- Custom Form Templates system
- Document Scanner endpoints
- Flask-FastAPI bridge (api_client.py)

### 🔜 NEXT: Phase 4 - Tier 2 Groq + RAG
1. Integrate Groq AI into /ai/query endpoint
2. Connect RAG knowledge base (brain/knowledge.py)
3. Implement smart routing between tiers

### Future Phases
- Phase 5: Tier 3 Claude/GPT with failover
- Phase 6: Master Architect self-healing

---

## What's Done (Don't Redo)

### Backend Infrastructure (NEW - Dec 8, 2025)
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
| `SESSION-LOG.md` | **Detailed session history - successes, failures, learnings** |
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

# Supabase PostgreSQL (✅ CONNECTED)
$env:DATABASE_URL='postgresql://postgres:PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres'

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
**Date:** December 14, 2025
**Completed:**
- ✅ **Control Center Redesign** - Complete rewrite with sidebar + detail panel layout
  - 11 positions (added Admin Assistant, Sales Rep, Owner/Principal)
  - All buttons functional (mode toggle, function cards, form cards, export, genie)
  - Dynamic position selection updates header, forms, and confidence
- ✅ **Data Central Page** - New document hub with AI extraction
  - Role-based filtering, document categories, upload modal
  - Compare versions, PDF viewer, version history, SOV modal
  - AI Analyze All with loading states
- ✅ **Backend Graceful Startup** - Database connection no longer crashes app
  - `init_database()` returns bool, prints helpful errors
  - Backend runs in demo mode when DB unavailable
- ✅ **Button Functionality** - 30+ buttons now working across both pages
  - Modals for forms, reviews, uploads, comparisons
  - Notification system for user feedback
  - Loading states and completion messages

**Next Session Should:**
1. **Connect forms to database** - Save/load from form_submissions table
2. **Implement document upload** - Backend endpoint + frontend integration
3. **Add Groq AI chat** - Real responses in Genie panel
4. **Test all 3 pages end-to-end** - Control Center, Data Central, Digital Foreman
5. Phase 4: Tier 2 Groq + RAG integration

**Key Files Changed:**
- `roofing_intelligence/templates/control_center.html` - Full redesign with 11 positions + JS
- `roofing_intelligence/templates/data_central.html` - New page with full functionality
- `roofing_intelligence/app.py` - Added /data-central route
- `roofio-backend/common/database.py` - Graceful init_database()
- `roofio-backend/main.py` - Handle graceful startup
- `SESSION-LOG.md` - Full session log with outstanding items

---

## Contact

For questions about the project, check:
1. This file first
2. `README.md` for features/structure
3. `NEXT-SESSION-BACKEND-MASTERPLAN.md` for backend details
4. `CLAUDE.md` for CAD Observer context
