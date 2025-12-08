# APPIO - Roofing Company Operating System

> **UI COMPLETE - v3.0 Milestone** | December 2024

AI-powered construction platform for Division 07 professionals. Role-based dashboards, document analysis, tiered AI processing, and 28+ integrations.

---

## Quick Start

```bash
cd roofing_intelligence
pip install flask PyPDF2 ezdxf groq
python app.py
# Open http://127.0.0.1:5000
```

---

## Claude Code Users

**IMPORTANT:** Before starting any work, read `CLAUDE-INSTRUCTIONS.md` for current priorities and context.

---

## Features Overview

### 9 Application Pages

| Route | Page | Description |
|-------|------|-------------|
| `/dashboard` | Company Dashboard | 6 role-based seats with traffic light status |
| `/analysis` | Document Analysis | Multi-file upload with smart roof filtering |
| `/roofio` | Roofio AI | Division 07 expert chat with 14 skill domains |
| `/control-center` | Control Center | 8 positions with Full AI/Assist/Off toggles |
| `/digital-foreman` | Digital Foreman | Risk Shield field documentation system |
| `/integrations` | Integrations Hub | 28+ connectors (email, storage, accounting, etc.) |
| `/projects` | Projects | Saved project management |
| `/inspector/<id>` | Guest Inspector | No-account access for hold point inspections |
| `/phone` | Phone | Hive 215 integration (planned) |

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

### Roofio Skills (14 Domains)

- **Standards**: FM Global, NRCA, SPRI, IIBEC, ASCE 7
- **Technical**: Roofing Systems, Wind Uplift, Leak Detection
- **Code**: IRC/ICC Codes, Standards Hierarchy
- **Testing**: Division 07 Testing, Inspections
- **Tools**: Web Scraper, ASCE 7 Hazard Tool, Drafting Innovations
- **Manufacturers**: Product specifications and warranty details

### Document Processing

- **Smart Roof Filter**: AI identifies roofing-relevant pages (60-80% cost savings)
- **Multi-File Upload**: Drawings, assemblies, specs, scopes
- **Real-Time Progress**: Server-Sent Events (SSE) streaming
- **DXF Generation**: AutoCAD-ready detail drawings
- **PDF Parsing**: Construction document extraction

### Integrations Hub (28+ Connectors)

| Category | Services |
|----------|----------|
| Email | Gmail, Outlook, Yahoo |
| Storage | Dropbox, Google Drive, OneDrive, Box |
| Accounting | QuickBooks, Xero, FreshBooks, Sage |
| Construction | Procore, Buildertrend, CoConstruct |
| Phone | Hive 215, RingCentral, Dialpad |
| CRM | Salesforce, HubSpot, Zoho |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask (Python 3.9+) |
| Frontend | Vanilla JS, CSS3 |
| UI Design | Glass morphism, dark/light themes |
| Real-time | Server-Sent Events (SSE) |
| PDF | PyPDF2 |
| CAD | ezdxf |
| AI | Groq (Llama 3), Anthropic Claude |

---

## Dependencies

```bash
# Core
flask>=2.0
PyPDF2>=3.0
ezdxf>=1.0

# AI (optional - for Roofio chat)
groq>=0.4

# Future Backend (Modal deployment)
upstash-redis
upstash-vector
sqlalchemy
python-jose
passlib
cryptography
```

---

## Project Structure

```
cad_observer/
├── roofing_intelligence/           # Main application
│   ├── app.py                      # Flask routes & API
│   ├── templates/                  # 9 HTML pages
│   │   ├── dashboard.html          # Company dashboard
│   │   ├── index.html              # Document analysis
│   │   ├── roofio.html             # AI chat interface
│   │   ├── control_center.html     # 8 position control
│   │   ├── digital_foreman.html    # Field documentation
│   │   ├── integrations.html       # 28+ connectors
│   │   ├── projects.html           # Project management
│   │   ├── inspector.html          # Guest inspector
│   │   └── phone.html              # Phone integration
│   ├── static/
│   │   ├── css/styles.css          # Main styles
│   │   ├── css/dashboard.css       # Dashboard styles
│   │   ├── js/app.js               # Analysis logic
│   │   ├── js/dashboard.js         # Dashboard logic
│   │   └── images/logo.png         # APPIO logo
│   ├── parsers/                    # Document parsers
│   │   ├── roof_page_filter.py     # Smart page filtering
│   │   ├── arch_drawing_parser.py  # Drawing analysis
│   │   ├── assembly_parser.py      # Assembly letters
│   │   ├── spec_parser.py          # Specifications
│   │   ├── scope_parser.py         # Scope of work
│   │   ├── pdf_extractor.py        # PDF extraction
│   │   └── text_cleaner.py         # Text utilities
│   ├── generators/
│   │   └── dxf_generator.py        # AutoCAD DXF output
│   ├── architect_ai/               # Tiered AI routing
│   │   └── rules_engine.py         # Query routing logic
│   └── roofio/                     # Roofio platform
│       ├── groq_client.py          # Groq AI integration
│       ├── skills/                 # 14 skill SKILL.md files
│       └── platform/               # Backend architecture
│           ├── schema.sql          # Database schema
│           ├── digital_foreman/    # Risk Shield system
│           ├── positions/          # 8 position system
│           ├── badges/             # Badge system
│           ├── confidence/         # Confidence scoring
│           └── forms/              # Form system
├── scripts/                        # CAD Observer tools
│   ├── click_capture.py            # Screenshot capture
│   ├── floating_toolbar.py         # Control toolbar
│   └── cad_task.py                 # AutoCAD task bridge
├── CLAUDE.md                       # Claude Code context
├── CLAUDE-INSTRUCTIONS.md          # Session instructions
└── NEXT-SESSION-BACKEND-MASTERPLAN.md  # Backend roadmap
```

---

## API Endpoints

### Document Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Start document analysis |
| GET | `/api/progress/<id>` | SSE progress stream |
| POST | `/api/project/save` | Save analysis results |
| GET | `/api/project/load/<file>` | Load saved project |
| DELETE | `/api/project/delete/<file>` | Delete project |

### Company Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/company/projects` | CRUD projects |
| GET/POST | `/api/company/activity` | Activity feed |
| GET | `/api/company/seats` | Role statuses |
| GET | `/api/company/metrics` | Dashboard metrics |

---

## Changelog

### v3.0 - UI Complete (December 2024)
- Added Control Center with 8 positions and AI mode toggles
- Added Digital Foreman with Risk Shield architecture
- Added Integrations Hub with 28+ service connectors
- Added Roofio AI chat with 14 skill domains
- Added Guest Inspector mode for hold point access
- Updated navigation across all pages
- Cleaned up 52 auto-generated HTML files
- Platform architecture specifications complete

### v2.0 - Company Dashboard
- APPIO branding with new logo
- 6 role-based seats (PM, Estimator, Operations, Accounting, Superintendent, Shop Drawings)
- Traffic light status indicators
- Task queues and project cards
- Activity feed with real-time updates
- Architect AI rules engine foundation

### v1.0 - Document Analysis
- Smart PDF roof page filtering
- Multi-layered element detection
- Assembly letter parsing
- DXF generation
- Real-time SSE progress

---

## Next Steps (Backend)

See `NEXT-SESSION-BACKEND-MASTERPLAN.md` for detailed implementation:

1. **Phase 1**: Security foundation (JWT, RBAC, OAuth)
2. **Phase 2**: Tier 1 Python layer (UPO, Foreman, Control)
3. **Phase 3**: Tier 2 Groq + RAG integration
4. **Phase 4**: Tier 3 Advanced LLM with failover
5. **Phase 5**: Master Architect self-healing

---

## CAD Observer (Original Feature)

AI-powered CAD workflow observation for AutoCAD:

```bash
python scripts/click_capture.py -p "Project Name"
```

AutoCAD LISP commands:
- `CAD-OBSERVER-START` - Start logging
- `CAD-OBSERVER-STOP` - Stop logging
- `CAD-OBSERVER-TASK` - Check for Claude tasks

---

## License

Proprietary - Lefebvre Design Solutions

---

## Support

- **Owner**: Armand (20+ year journeyman roofer/waterproofer, Local 30)
- **Spec Sections**: 07 62 00, 07 50 00, 07 27 00, 07 92 00
- **CAD**: AutoCAD LT for shop drawings
