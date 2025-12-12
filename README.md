# CAD Observer Repository

> **3 Applications in 1 Repo** | Last Updated: December 12, 2024

This repository contains three distinct applications for Armand Lefebvre (20+ year journeyman roofer/waterproofer, Local 30):

---

## Applications Overview

| Application | Purpose | Status |
|-------------|---------|--------|
| **CAD Observer** | Watches AutoCAD workflow to learn patterns | ✅ Production Ready |
| **APPIO** | Roofing company operating system (9 pages) | ✅ UI Complete |
| **ROOFIO Backend** | Unified data infrastructure & tiered AI | ⏳ Phase 1 Done |

---

## Status Matrix

```
CAD Observer        [████████████████████] 100% - Ready to use
APPIO UI            [████████████████████] 100% - All 9 pages working
Document Processing [████████████████████] 100% - PDFs, DXF export
Roofio AI Skills    [████████████████████] 100% - 14 domains
Backend Security    [████████████████████] 100% - Phase 1 done
Backend Database    [████████████████████] 100% - Tables created!
Backend API Layer   [████████████░░░░░░░░]  60% - CRUD ready
```

---

# Application 1: CAD Observer

**Purpose:** AI-powered observation of AutoCAD shop drawing workflows
**Location:** `scripts/` + `CLAUDE.md`
**Storage:** `~/.cad-observer/observations.jsonl`

### Components

| Script | Description |
|--------|-------------|
| `click_capture.py` | Screenshot capture on mouse clicks with XY coordinates |
| `research_capture.py` | Capture mode for spec sheets/literature |
| `floating_toolbar.py` | UI control panel for all modes |
| `cad-observer.lsp` | AutoCAD LISP plugin for bidirectional tasks |
| `cad_task.py` | Python bridge to send commands to AutoCAD |

### Quick Start

```bash
# Click capture mode (CAD work)
python scripts/click_capture.py --project "Project Name"

# Research capture mode (specs/literature)
python scripts/research_capture.py --project "Project Name"

# All-in-one toolbar
python scripts/floating_toolbar.py --project "Project Name"
```

### AutoCAD LISP Commands

Load `scripts/cad-observer.lsp` in AutoCAD:

| Command | Action |
|---------|--------|
| `CAD-OBSERVER-START` | Start logging session |
| `CAD-OBSERVER-STOP` | Stop logging session |
| `CAD-OBSERVER-STATUS` | Show current status |
| `CAD-OBSERVER-TASK` | Check for Claude tasks |
| `CAD-OBSERVER-AUTO` | Toggle auto-task execution |

### Key Protocol

**Question-First:** When observing CAD work, Claude MUST:
1. Describe what it sees factually
2. Ask 2-3 questions before logging
3. Wait for user response
4. Log with confirmed intent

---

# Application 2: APPIO - Roofing Intelligence Platform

**Purpose:** Complete roofing company operating system with AI
**Location:** `roofing_intelligence/`
**Run:** `python roofing_intelligence/app.py` → http://127.0.0.1:5000

### Quick Start

```bash
cd roofing_intelligence
pip install flask PyPDF2 ezdxf groq
python app.py
# Open http://127.0.0.1:5000
```

### 9 Application Pages

| Route | Page | Description |
|-------|------|-------------|
| `/dashboard` | Company Dashboard | 6 role-based seats with traffic light status |
| `/analysis` | Document Analysis | Multi-file upload with smart roof filtering |
| `/roofio` | Roofio AI | Division 07 expert chat with 14 skill domains |
| `/control-center` | Control Center | 8 positions with Full AI/Assist/Off toggles |
| `/digital-foreman` | Digital Foreman | Risk Shield field documentation system |
| `/integrations` | Integrations Hub | 28+ connectors (QuickBooks, Procore, etc.) |
| `/projects` | Projects | Saved project management |
| `/inspector/<id>` | Guest Inspector | No-account access for hold point inspections |
| `/phone` | Phone | Hive 215 integration (planned) |

### Document Processing Pipeline

| Parser | Lines | Purpose |
|--------|-------|---------|
| `roof_page_filter.py` | 485 | Smart AI filtering (60-80% cost savings) |
| `arch_drawing_parser.py` | 546 | Extract drawing references |
| `assembly_parser.py` | 406 | Parse assembly letters |
| `spec_parser.py` | 50 | Specification extraction |
| `scope_parser.py` | 66 | Work scope analysis |
| `dxf_generator.py` | 403 | AutoCAD-ready DXF export |

### Roofio AI Skills (14 Domains)

- **Standards**: FM Global, NRCA, SPRI, IIBEC, ASCE 7
- **Technical**: Roofing Systems, Wind Uplift, Leak Detection
- **Code**: IRC/ICC Codes, Standards Hierarchy
- **Testing**: Division 07 Testing, Inspections
- **Tools**: Web Scraper, ASCE 7 Hazard Tool, Drafting Innovations
- **Manufacturers**: Carlisle, Firestone, GAF product specs

### Tiered AI Architecture

```
                    ▲ Claude/GPT (Tier 3) - $15-75/1M tokens
                   ╱ ╲ Complex reasoning - 1% of queries
                  ╱───╲
                 ╱ Groq ╲ $0.64/1M tokens (Tier 2)
                ╱  4%    ╲ 300+ tok/sec - NLP tasks
               ╱──────────╲
              ╱  Python    ╲ ~$0.00 (Tier 1)
             ╱    95%       ╲ CRUD, retrieval, logic
            ╱────────────────╲
```

### 8-Position System

| Position | AI Modes | Description |
|----------|----------|-------------|
| Estimator | Full/Assist/Off | Takeoffs, pricing, proposals |
| Project Manager | Full/Assist/Off | Scheduling, coordination |
| QC Manager | Full/Assist/Off | Quality control, inspections |
| Safety Director | Full/Assist/Off | JHA, compliance, training |
| Superintendent | Full/Assist/Off | Field operations |
| Shop Drawings | Full/Assist/Off | CAD details, submittals |
| Accounting | Full/Assist/Off | Invoicing, payroll |
| Operations | Full/Assist/Off | Logistics, resources |

### Integrations Hub (28+ Connectors)

| Category | Services |
|----------|----------|
| Email | Gmail, Outlook, Yahoo |
| Storage | Dropbox, Google Drive, OneDrive, Box |
| Accounting | QuickBooks, Xero, FreshBooks, Sage |
| Construction | Procore, Buildertrend, CoConstruct |
| Phone | Hive 215, RingCentral, Dialpad |
| CRM | Salesforce, HubSpot, Zoho |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Start document analysis |
| GET | `/api/progress/<id>` | SSE progress stream |
| POST | `/api/project/save` | Save analysis results |
| GET | `/api/project/load/<file>` | Load saved project |
| DELETE | `/api/project/delete/<file>` | Delete project |
| GET/POST | `/api/company/projects` | CRUD projects |
| GET/POST | `/api/company/activity` | Activity feed |
| GET | `/api/company/seats` | Role statuses |
| GET | `/api/company/metrics` | Dashboard metrics |

---

# Application 3: ROOFIO Backend

**Purpose:** Unified data infrastructure with tiered AI architecture
**Location:** `roofio-backend/`
**Status:** Phase 1 Complete (Security Foundation)

### Infrastructure Status

| Service | Status | Details |
|---------|--------|---------|
| Upstash Redis | ✅ Ready | Sessions, rate limiting, audit logging |
| Upstash Vector | ✅ Ready | Hybrid index (384 dim), RAG knowledge base |
| Groq API | ✅ Ready | Llama 3.3 70B, ~395ms response time |
| Supabase PostgreSQL | ✅ Ready | Connected via pooler (IPv4 compatible) |

### Phase 1 Complete - Security Foundation

| File | Lines | Purpose |
|------|-------|---------|
| `common/config.py` | 272 | Environment + Upstash credentials |
| `common/security.py` | 911 | JWT, OAuth (4 providers), RBAC (5 roles), encryption |
| `common/session.py` | 314 | Redis-backed session management |
| `common/database.py` | 323 | SQLAlchemy async + PostgreSQL multi-tenant |

### Test Scripts

```bash
cd roofio-backend
python test_redis.py      # Upstash Redis connectivity
python test_vector.py     # Vector DB search
python test_groq.py       # Groq API integration
python test_postgres.py   # Supabase PostgreSQL
```

### Environment Setup

Copy `.env.example` to `.env` and configure:

```
ROOFIO_ENV=development

# Upstash
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...
UPSTASH_VECTOR_REST_URL=...
UPSTASH_VECTOR_REST_TOKEN=...

# Database
DATABASE_URL=postgresql://...

# Security
JWT_SECRET=...
ENCRYPTION_KEY=...

# AI Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

### Backend Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Done | Security foundation (JWT, RBAC, OAuth, encryption) |
| Phase 2 | 🔜 Next | Tier 1 Python CRUD (users, agencies, projects) |
| Phase 3 | 🔜 | Tier 2 Groq + RAG integration |
| Phase 4 | 🔜 | Tier 3 Claude/GPT with failover |
| Phase 5 | 🔜 | Master Architect self-healing |

---

# Project Structure

```
cad_observer/
├── scripts/                           # CAD OBSERVER
│   ├── click_capture.py               # Screenshot on click
│   ├── research_capture.py            # Spec capture mode
│   ├── floating_toolbar.py            # UI toolbar
│   ├── cad-observer.lsp               # AutoCAD plugin
│   └── cad_task.py                    # Python ↔ AutoCAD bridge
│
├── roofing_intelligence/              # APPIO
│   ├── app.py                         # Flask routes (1,003 lines)
│   ├── templates/                     # 9 HTML pages
│   ├── static/                        # CSS + JS
│   ├── parsers/                       # Document processing (2,100 lines)
│   ├── generators/                    # DXF output
│   ├── architect_ai/                  # Tiered AI routing
│   └── roofio/                        # Platform core
│       ├── groq_client.py             # Groq integration
│       ├── skills/                    # 14 skill domains (7,296 lines)
│       └── platform/                  # Backend specs
│           ├── forms/                 # 74 forms
│           ├── positions/             # 8 positions
│           ├── confidence/            # AI scoring
│           ├── badges/                # Badge system
│           └── digital_foreman/       # Risk Shield
│
├── roofio-backend/                    # ROOFIO BACKEND
│   ├── common/                        # Phase 1 complete
│   │   ├── config.py                  # Environment config
│   │   ├── security.py                # JWT, OAuth, RBAC
│   │   ├── session.py                 # Redis sessions
│   │   └── database.py                # PostgreSQL async
│   ├── tier1/                         # Placeholder
│   ├── tier2/                         # Placeholder
│   ├── tier3/                         # Placeholder
│   ├── brain/                         # RAG placeholder
│   ├── architect/                     # Meta-AI placeholder
│   └── test_*.py                      # Integration tests
│
├── drop/                              # Archive/experimental
│   ├── architect-ai-skill/            # Meta-intelligence docs
│   ├── roofio-complete-skills/        # Skill reference (14 domains)
│   ├── security_backend/              # Phase 1 source
│   └── training-data-collection-skill/
│
├── README.md                          # This file
├── CLAUDE.md                          # CAD Observer context
├── CLAUDE-INSTRUCTIONS.md             # Current session priorities
└── NEXT-SESSION-BACKEND-MASTERPLAN.md # Backend roadmap
```

---

# Dependencies

```bash
# CAD Observer
pip install pynput pillow

# APPIO
pip install flask PyPDF2 ezdxf groq

# ROOFIO Backend
pip install upstash-redis upstash-vector asyncpg sqlalchemy python-jose cryptography httpx
```

---

# Tech Stack Summary

| Layer | Technology | Used By |
|-------|------------|---------|
| CAD Integration | AutoCAD LISP + Python | CAD Observer |
| Screenshots | pynput + Pillow | CAD Observer |
| Web Framework | Flask | APPIO |
| PDF Processing | PyPDF2 | APPIO |
| CAD Export | ezdxf | APPIO |
| Frontend | Vanilla JS + CSS3 | APPIO |
| Real-time | Server-Sent Events (SSE) | APPIO |
| Sessions | Upstash Redis | Backend |
| Vector DB | Upstash Vector (384 dim) | Backend |
| Database | Supabase PostgreSQL | Backend |
| Tier 2 AI | Groq Llama 3.3 70B | Backend |
| Tier 3 AI | Anthropic Claude / OpenAI | Backend |
| Auth | JWT + OAuth + Fernet | Backend |

---

# Changelog

### December 12, 2024 - Repository Restructure
- Documented 3 distinct applications in README
- Added status matrix and completion tracking
- Clarified boundaries between CAD Observer, APPIO, and Backend

### December 8, 2024 - Backend Phase 1 Complete
- Security foundation (JWT, RBAC, OAuth, encryption)
- Upstash Redis and Vector integration
- Groq API tested and working

### December 2024 - APPIO UI Complete
- All 9 pages functional
- 8-position Control Center
- Digital Foreman Risk Shield
- 28+ integration connectors
- 14 Roofio AI skill domains

### Earlier - CAD Observer & Document Analysis
- Click capture with coordinates
- AutoCAD LISP bidirectional tasks
- Smart PDF roof page filtering
- DXF generation

---

# License

Proprietary - Lefebvre Design Solutions

---

# Support

- **Owner**: Armand (20+ year journeyman roofer/waterproofer, Local 30)
- **Spec Sections**: 07 62 00, 07 50 00, 07 27 00, 07 92 00
- **CAD**: AutoCAD LT for shop drawings
