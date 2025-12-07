# APPIO - Next Claude Code Session Guide

**Last Updated**: December 2024
**Status**: Phase 1 Complete - Company Dashboard UI

---

## Quick Context

APPIO is a roofing company operating system with:
- Role-based dashboard (PM, Estimator, Operations, Accounting, Field, Shop Drawings)
- Document analysis with smart roof page filtering
- Tiered AI system (Python → Groq → Anthropic)
- Training data collection for fine-tuning
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
- Architect AI rules engine foundation (Tier 0 Python)
- README.md documentation
- Session continuation guide

---

## TODO List for Next Session

### Priority 1: Training Data Collection System
Based on `drop/training-data-collection-skill/`:

- [ ] Create `roofing_intelligence/architect_ai/training_collector.py`
- [ ] Implement `TrainingCollector` class with:
  - [ ] `capture()` - Auto-capture query/response pairs
  - [ ] `add_feedback()` - Track thumbs up/down
  - [ ] `record_correction()` - Capture user corrections (high value!)
  - [ ] `get_stats()` - Collection statistics
  - [ ] `export_for_training()` - Export for Modal
- [ ] Add auto-tagging with roofing domain keywords
- [ ] Add domain relevance scoring (high/medium/low)
- [ ] Create training data dashboard widget showing:
  - Total examples collected
  - Corrections count
  - By source breakdown
  - Export button

### Priority 2: Groq API Integration (Tier 1)
- [ ] Add Groq client to `architect_ai/`
- [ ] Implement `handle_tier_1_groq()` in rules_engine.py
- [ ] Add Groq API key to environment variables
- [ ] Route NLP tasks to Groq:
  - RFI generation
  - Summarization
  - General explanations
- [ ] Add cost tracking per query

### Priority 3: Skill Loading System
Based on skill packages in `drop/`:

- [ ] Create `architect_ai/skill_loader.py`
- [ ] Parse SKILL.md files for each role
- [ ] Load role-specific context when seat is activated
- [ ] Skills to integrate:
  - [ ] `roofing-pm-skills` (12 sub-skills)
  - [ ] `roofing skills` (role-specific)
  - [ ] `shop-drawing-skill` (CAD standards)
  - [ ] `architect-ai-skill` (meta-AI routing)
  - [ ] `training-data-collection-skill` (training pipeline)

### Priority 4: Dashboard Enhancements
- [ ] Add Architect AI widget showing:
  - Tier distribution pie chart
  - Cost savings vs all-Anthropic
  - Query latency metrics
- [ ] Add training data collection widget
- [ ] Make project cards link to detail pages (not just modal)
- [ ] Connect to real database (SQLite or PostgreSQL)

### Priority 5: Phone Integration (Hive 215)
- [ ] Research Hive 215 API documentation
- [ ] Create `roofing_intelligence/phone_integration/`
- [ ] Implement click-to-call from contacts
- [ ] Add call logging with project linking
- [ ] AI call transcription (future)

---

## Key Files Reference

### Templates
```
roofing_intelligence/templates/
├── dashboard.html   # Company dashboard (/dashboard)
├── index.html       # Document analysis (/analysis)
├── projects.html    # Project management (/projects)
└── phone.html       # Phone integration (/phone)
```

### Architect AI
```
roofing_intelligence/architect_ai/
├── __init__.py
├── rules_engine.py      # Tier 0 Python rules, routing
├── training_collector.py  # TODO: Training data collection
├── groq_client.py         # TODO: Tier 1 Groq integration
└── skill_loader.py        # TODO: Load SKILL.md per role
```

### Skills (in drop/)
```
drop/
├── architect-ai-skill/              # Tiered routing docs
├── training-data-collection-skill/  # Training pipeline docs
├── roofing-pm-skills.zip            # 12 PM sub-skills
├── roofing skills.zip               # Role-specific skills
└── shop-drawing-skill.zip           # CAD standards
```

---

## Architecture

### Tiered AI System
```
┌─────────────────────────────────────────────────────────┐
│                    INCOMING QUERY                        │
└────────────────────────┬────────────────────────────────┘
                         │
                    route_query()
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │  Tier 0  │   │  Tier 1  │   │  Tier 2  │
   │  Python  │   │   Groq   │   │ Anthropic│
   │   Rules  │   │   NLP    │   │ Complex  │
   │   FREE   │   │ $0.0001  │   │  $0.01   │
   │  <50ms   │   │  500ms   │   │   2s     │
   │   60%    │   │   35%    │   │   5%     │
   └──────────┘   └──────────┘   └──────────┘
```

### Training Data Flow
```
┌─────────────────────────────────────────────────────────┐
│              PRODUCTION QUERIES                          │
└────────────────────────┬────────────────────────────────┘
                         │
                    capture()
                         │
                         ▼
              ┌──────────────────┐
              │  TrainingCollector│
              │  - Auto-tag       │
              │  - Score relevance│
              │  - Buffer/Flush   │
              └────────┬─────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ Feedback │  │Corrections│  │  Export  │
   │ positive │  │ VERY HIGH │  │ to Modal │
   │ negative │  │  VALUE    │  │ training │
   └──────────┘  └──────────┘  └──────────┘
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
- `GET /api/company/metrics` - Dashboard metrics

### TODO: Training Data
- `GET /api/training/stats` - Collection statistics
- `POST /api/training/feedback` - Record feedback
- `POST /api/training/correction` - Record correction
- `POST /api/training/export` - Export for Modal

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

# Merge to main (after testing)
git checkout main
git merge claude/feature-name-sessionId
git push origin main
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
- [ ] Python syntax valid (`python -m py_compile app.py`)

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

Example:
> "I'm continuing work on APPIO. Read CLAUDE_SESSION.md for context.
> Next task: Implement the training data collection system from Priority 1"
