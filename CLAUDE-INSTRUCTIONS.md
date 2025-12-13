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
**Date:** December 13, 2025
**Completed:**
- ✅ **Database Cleanup & Build** - Unified schema created
- ✅ **Codebase Cleanup** - Removed 9,428 lines of duplicate code from drop folder
- ✅ **Fixed config.py** - Removed hardcoded "roofio" defaults
- ✅ **Fixed init_db.py** - Standalone script with raw SQL (no import issues)
- ✅ **Created unified_schema.sql** - 9 tables, standardized `agency_id` naming
- ✅ **Moved tier3 files** - knowledge.py, master_architect.py, modal_app.py, security.py
- ✅ **VS Code debug config** - "Init Database" added to launch.json
- ✅ **Supabase tables created** - All 9 tables successfully initialized:
  - agencies, users, clients, projects
  - form_templates, form_submissions
  - ai_action_logs, audit_logs, position_configs

**Next Session Should:**
1. **Test the Dashboard UI** - Verify new backend tables work with UI
2. Phase 4: Tier 2 Groq + RAG integration
3. Connect Digital Foreman to form submission API
4. Connect Inspector page to form submission API
5. Add file upload handling for scan endpoint

**Key Files Changed:**
- `roofio-backend/database/unified_schema.sql` - Authoritative DB schema
- `roofio-backend/init_db.py` - Standalone DB init script
- `roofio-backend/common/config.py` - No more hardcoded defaults
- `roofio-backend/tier3/` - Moved master_architect, knowledge, modal_app, security

---

## Contact

For questions about the project, check:
1. This file first
2. `README.md` for features/structure
3. `NEXT-SESSION-BACKEND-MASTERPLAN.md` for backend details
4. `CLAUDE.md` for CAD Observer context
