# APPIO - Intelligent Construction Platform

**AI-powered roofing company operating system with role-based dashboards, document analysis, and tiered AI processing.**

---

## Features

### Company Dashboard (`/dashboard`)
- **Role-Based Seats**: PM, Estimator, Operations, Accounting, Superintendent, Shop Drawings
- **Traffic Light Status**: Red/Yellow/Green indicators for project health
- **Task Queues**: Urgent, pending, and completed tasks per role
- **Company Metrics**: Active projects, pending bids, roadblocks, revenue MTD
- **Project Cards**: Contract value, phase, progress bars, assignees
- **Activity Feed**: Real-time updates across all operations
- **New Project Modal**: Quick project creation with form validation

### Document Analysis (`/analysis`)
- **Multi-File Upload**: Drag & drop for drawings, assemblies, specs, scopes
- **Smart Roof Filter**: AI identifies roofing-relevant pages (saves 60-80% processing)
- **Real-Time Progress**: Server-Sent Events (SSE) for live status updates
- **DXF Generation**: Auto-generate AutoCAD-ready detail drawings
- **PDF Parsing**: Extract and categorize content from construction documents

### Project Management (`/projects`)
- **Saved Projects**: View all analyzed projects with metadata
- **Project Details Modal**: Full analysis results, document counts, cost savings
- **View/Delete Actions**: Manage projects with confirmation dialogs
- **Filter Options**: All, Active, Completed project views

### Phone Integration (`/phone`)
- **Coming Soon**: Hive 215 business phone integration
- **Planned Features**: Click-to-call, AI transcription, automatic project linking

### Architect AI (Backend)
- **Tiered Query Routing**:
  - **Tier 0 (Python)**: Direct lookups, calculations - FREE, <50ms
  - **Tier 1 (Groq)**: NLP tasks, document generation - $0.0001/query
  - **Tier 2 (Anthropic)**: Complex reasoning - $0.01/query
- **Industry Data Tables**: Production rates, material coverage, waste factors
- **Cost Optimization**: Target 95% savings vs all-Tier-2

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask (Python) |
| Frontend | Vanilla JS, CSS3 |
| UI Design | Glass morphism, dark/light themes |
| Real-time | Server-Sent Events (SSE) |
| PDF Processing | PyPDF2 |
| CAD Generation | ezdxf |

---

## Installation

```bash
# Clone repository
git clone https://github.com/jenkintownelectricity/cad_observer.git
cd cad_observer/roofing_intelligence

# Install dependencies
pip install flask PyPDF2 ezdxf

# Run application
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## Project Structure

```
cad_observer/
├── roofing_intelligence/
│   ├── app.py                    # Main Flask application
│   ├── architect_ai/
│   │   ├── __init__.py
│   │   └── rules_engine.py       # Tiered AI routing
│   ├── parsers/                  # Document parsers
│   ├── generators/               # DXF generators
│   ├── static/
│   │   ├── css/                  # Stylesheets
│   │   ├── js/                   # JavaScript
│   │   └── images/               # Logo and assets
│   └── templates/                # HTML templates
├── drop/                         # Skill packages
│   ├── architect-ai-skill/
│   ├── roofing-pm-skills.zip
│   ├── roofing skills.zip
│   └── shop-drawing-skill.zip
├── scripts/                      # CAD Observer scripts
├── CLAUDE.md                     # Claude Code instructions
└── CLAUDE_SESSION.md             # Session continuation guide
```

---

## Routes

| Route | Description |
|-------|-------------|
| `/` | Redirects to `/dashboard` |
| `/dashboard` | Company dashboard with role seats |
| `/analysis` | Document upload and analysis |
| `/projects` | Saved project management |
| `/phone` | Phone integration (coming soon) |

---

## Changelog (v2.0)

### Added
- APPIO branding with new logo
- Company Dashboard with 6 role-based seats
- Traffic light status indicators (red/yellow/green)
- Task queue components per role
- Project cards with progress tracking
- Activity feed with real-time updates
- Architect AI rules engine foundation
- Tiered query routing system
- Production rates and material coverage data
- Consistent navigation across all pages

### Fixed
- Navigation inconsistency between pages
- Project click redirecting to wrong page
- File upload button click handlers
- "Read of closed files" threading error
- Logo not clickable on some pages

### Changed
- `/` now redirects to `/dashboard`
- Rebranded from "RoofingOS" to "APPIO"
- Unified header design across all templates

---

## CAD Observer (Original Feature)

AI-powered CAD workflow observation system for AutoCAD:

```bash
# Start click capture
python scripts/click_capture.py -p "Project Name"

# AutoCAD commands
CAD-OBSERVER-START   # Start logging
CAD-OBSERVER-STOP    # Stop logging
CAD-OBSERVER-TASK    # Check for Claude tasks
```

---

## License

Proprietary - Lefebvre Design Solutions
