# APPIO - Next Claude Code Session Guide

**Last Updated**: December 2024
**Status**: Phase 1 Complete - Company Dashboard UI

---

## Quick Context

APPIO is a roofing company operating system with:
- Role-based dashboard (PM, Estimator, Operations, Accounting, Field, Shop Drawings)
- Document analysis with smart roof page filtering
- Tiered AI system (Python → Groq → Anthropic)
- APPIO branding with futuristic construction logo

---

## Current State

### Completed (Phase 1)
- Company Dashboard with 6 role-based "seats"
- Traffic light status indicators (red/yellow/green)
- Task queues per role (urgent/pending/completed)
- Project cards with progress tracking
- Activity feed with real-time updates
- APPIO logo integrated on all pages
- Consistent navigation across all templates
- Architect AI rules engine foundation

### In Progress
- Architect AI dashboard widget (showing tier distribution, cost savings)
- Skill integration (loading SKILL.md files as context)

### Next Phases
- **Phase 2**: Integrate skill system (load SKILL.md as context per role)
- **Phase 3**: Implement tiered AI backend (Python → Groq → Anthropic)
- **Phase 4**: Add Architect AI monitoring dashboard
- **Phase 5**: Hive 215 phone integration

---

## Key Files

### Templates (all use APPIO logo)
```
roofing_intelligence/templates/
├── dashboard.html   # Main company dashboard
├── index.html       # Document analysis (/analysis)
├── projects.html    # Project management
└── phone.html       # Phone integration (coming soon)
```

### Styles
```
roofing_intelligence/static/css/
├── styles.css       # Main styles, glass morphism, themes
└── dashboard.css    # Dashboard-specific (seats, traffic lights)
```

### JavaScript
```
roofing_intelligence/static/js/
├── app.js           # Analysis page functionality
└── dashboard.js     # Dashboard interactivity
```

### Architect AI
```
roofing_intelligence/architect_ai/
├── __init__.py
└── rules_engine.py  # Tier 0 Python rules, routing logic
```

### Skills (in drop/ folder)
```
drop/
├── architect-ai-skill/     # Extracted - tiered routing docs
├── roofing-pm-skills.zip   # 12 PM sub-skills
├── roofing skills.zip      # Role-specific skills
└── shop-drawing-skill.zip  # CAD standards
```

---

## Routes

| Route | Template | Description |
|-------|----------|-------------|
| `/` | - | Redirects to `/dashboard` |
| `/dashboard` | dashboard.html | Company dashboard |
| `/analysis` | index.html | Document analysis |
| `/projects` | projects.html | Saved projects |
| `/phone` | phone.html | Phone (coming soon) |

---

## API Endpoints

### Document Analysis
- `POST /api/analyze` - Start analysis
- `GET /api/progress/<id>` - SSE progress stream
- `POST /api/project/save` - Save results
- `GET /api/project/load/<file>` - Load project
- `DELETE /api/project/delete/<file>` - Delete project

### Company Dashboard
- `GET/POST /api/company/projects` - CRUD projects
- `GET/POST /api/company/activity` - Activity feed
- `GET /api/company/seats` - Role statuses
- `PUT /api/company/seats/<role>` - Update seat
- `GET /api/company/metrics` - Dashboard metrics

---

## Architecture Decisions

### Tiered AI System
```
Tier 0: Python Rules     → $0, <50ms      → 60% of queries
Tier 1: Groq             → $0.0001, 500ms → 35% of queries
Tier 2: Anthropic        → $0.01, 2s      → 5% of queries
```

### Routing Logic (rules_engine.py)
- Production rate lookups → Tier 0
- Material calculations → Tier 0
- Spec section lookups → Tier 0
- Document generation → Tier 1
- Summarization → Tier 1
- Complex reasoning → Tier 2

### UI Consistency
- All pages use same header with APPIO logo
- Navigation: Dashboard, Analysis, Projects, Phone
- Glass morphism design with dark/light themes
- Traffic lights: `.traffic-light.red/yellow/green`

---

## Known Issues / TODOs

### To Implement
- [ ] Architect AI dashboard widget (tier distribution chart)
- [ ] Groq API integration for Tier 1
- [ ] Anthropic fallback for Tier 2
- [ ] Skill loading system (parse SKILL.md per role)
- [ ] Real project database (currently sample data)
- [ ] Hive 215 phone API integration

### Potential Improvements
- [ ] WebSocket for real-time dashboard updates
- [ ] User authentication system
- [ ] Role-based permissions
- [ ] Project detail pages (not just modal)
- [ ] Mobile responsive improvements

---

## Development Commands

### Run App
```bash
cd roofing_intelligence
python app.py
# Open http://127.0.0.1:5000
```

### Git Workflow
```bash
# Create feature branch
git checkout -b claude/feature-name-sessionId

# Commit changes
git add -A
git commit -m "Description"

# Push
git push -u origin claude/feature-name-sessionId
```

---

## Testing Checklist

Before marking features complete:
- [ ] All 4 pages load without errors
- [ ] Logo appears and links to /dashboard
- [ ] Navigation active state correct per page
- [ ] Theme toggle works (dark/light)
- [ ] Modals open/close properly
- [ ] File uploads work on /analysis
- [ ] Project View/Delete buttons work
- [ ] No console errors

---

## Contact / Context

- **Owner**: Armand (20+ year journeyman roofer/waterproofer, Local 30)
- **Projects**: UMass waterproofing, JHU Library, commercial roofing
- **Spec Sections**: 07 62 00, 07 50 00, 07 27 00, 07 92 00
- **CAD**: AutoCAD LT for shop drawings

---

## Resume Prompt

To continue development, tell Claude:

> "I'm continuing work on APPIO. Read CLAUDE_SESSION.md for context.
> Next task: [describe what you want to build]"
