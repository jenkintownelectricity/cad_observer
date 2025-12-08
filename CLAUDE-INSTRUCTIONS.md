# Claude Code Session Instructions

> **READ THIS FIRST** - Always check this file at the start of every session.

---

## Current Status

| Item | Status |
|------|--------|
| **UI** | COMPLETE (v3.0) |
| **Backend** | NOT STARTED |
| **Database** | Schema designed, not deployed |
| **Deployment** | Local Flask only |

---

## Priority Queue

### NEXT UP: Backend Implementation

**Start here:** `NEXT-SESSION-BACKEND-MASTERPLAN.md`

**Phase 1 - Security Foundation** (Start with this)
```
Tell Claude: "Implement Phase 1 of Backend Master Plan - security.py foundation"
```

Files to create:
1. `roofio-backend/common/security.py` - JWT, OAuth, RBAC, encryption
2. `roofio-backend/common/session.py` - Redis-backed sessions
3. `roofio-backend/common/database.py` - PostgreSQL connection
4. `roofio-backend/common/config.py` - Environment config

### Future Phases
- Phase 2: Tier 1 Python layer (UPO, Foreman, Control modules)
- Phase 3: Tier 2 Groq + RAG integration
- Phase 4: Tier 3 Advanced LLM with failover
- Phase 5: Master Architect self-healing

---

## What's Done (Don't Redo)

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

```bash
# Upstash Redis
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...

# Database
DATABASE_URL=postgresql://...

# AI
GROQ_API_KEY=...
ANTHROPIC_API_KEY=...

# Security
JWT_SECRET=...
ENCRYPTION_KEY=...
```

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
- UI Complete milestone (v3.0)
- Updated navigation with Control Center, Foreman, Integrations
- Deleted 52 auto-generated HTML files
- Created comprehensive README
- Created this instructions file

**Next Session Should:**
1. Start Backend Phase 1 (security.py)
2. Set up Upstash Redis account
3. Create roofio-backend/ directory structure

---

## Contact

For questions about the project, check:
1. This file first
2. `README.md` for features/structure
3. `NEXT-SESSION-BACKEND-MASTERPLAN.md` for backend details
4. `CLAUDE.md` for CAD Observer context
