# Project Context and AI Agent Instructions

> **Single source of truth for Claude** | Last Updated: December 13, 2025

This document ensures consistent and high-quality contributions to the repository.

---

## 1. Core Mandates (MUST ADHERE)

### 1.1. Atomic Commits
All changes must be organized into **atomic commits**. A single commit must contain only changes related to one logical unit of work (e.g., one feature, one bug fix, one refactor).

### 1.2. Commit Message Standard
Use the **Conventional Commits** standard.

**Format:** `type(scope): subject`

| Type | Use When |
|------|----------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change (no bug fix, no new feature) |
| `style` | Formatting only |
| `chore` | Build, dependencies, config |
| `test` | Adding or updating tests |

**Examples:**
```
feat(backend): Add form submission API endpoint
fix(database): Remove hardcoded credential defaults
docs(readme): Add December 13 changelog entry
refactor(init_db): Use asyncpg directly instead of SQLAlchemy imports
```

### 1.3. Local Execution & Validation
Always propose a command to run tests before proposing code changes:

```bash
# Backend tests
cd roofio-backend && python -m pytest

# Frontend (APPIO)
cd roofing_intelligence && python app.py
# Then test at http://127.0.0.1:5000

# Database init
cd roofio-backend && python init_db.py
```

### 1.4. Context File Updates
If a major architectural decision is made, you **MUST** propose an update to this `CLAUDE.md` file in the same change request.

### 1.5. No Quick Fixes
**"NO QUICK FIXES. REAL FIX. DON'T BE A LAZY AI."** - Armand

- Fix root causes, not symptoms
- Validate environment before assuming it's correct
- Fail fast with helpful error messages
- Document why something broke, not just how you fixed it

---

## 2. Project Overview

### 2.1. Three Applications in One Repo

| Application | Location | Purpose | Run Command |
|-------------|----------|---------|-------------|
| **CAD Observer** | `scripts/` | AutoCAD workflow observation | `python scripts/floating_toolbar.py` |
| **APPIO** | `roofing_intelligence/` | Roofing company OS (9 pages) | `python roofing_intelligence/app.py` |
| **ROOFIO Backend** | `roofio-backend/` | Data infrastructure + AI | `uvicorn main:app --reload` |

### 2.2. Key Reference Files

| File | Purpose | Read When |
|------|---------|-----------|
| `CLAUDE.md` | This file - AI instructions | Every session |
| `SESSION-LOG.md` | Session history, problems, solutions | Every session |
| `README.md` | Full project documentation | Understanding project |
| `CLAUDE-INSTRUCTIONS.md` | Current priorities | Starting work |

---

## 3. Architectural Decisions & Constraints

### 3.1. Backend Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Framework | FastAPI | Async Python |
| Database | Supabase PostgreSQL | Via asyncpg |
| Sessions | Upstash Redis | REST API |
| Vector DB | Upstash Vector | 384 dimensions |
| Tier 2 AI | Groq Llama 3.3 70B | ~395ms response |
| Tier 3 AI | Claude / GPT | Fallback only |
| Auth | JWT + Fernet | Multi-tenant |

### 3.2. Frontend Stack (APPIO)

| Layer | Technology | Notes |
|-------|------------|-------|
| Framework | Flask | Python |
| Styling | Vanilla CSS | `styles.css` lines 2046-2238 for forms |
| JavaScript | Vanilla JS | `interactions.js`, `ux-utilities.js` |
| Real-time | Server-Sent Events | Progress streaming |

### 3.3. Database Conventions

**CRITICAL:** All tables use `agency_id` for multi-tenancy.

```sql
-- CORRECT
agency_id UUID REFERENCES agencies(agency_id)

-- WRONG (legacy naming)
organization_id, company_id, tenant_id
```

**Tables (9 total):**
- agencies, users, clients, projects
- form_templates, form_submissions
- ai_action_logs, audit_logs, position_configs

### 3.4. Environment Configuration

**NEVER use hardcoded defaults for credentials:**

```python
# CORRECT - Fail fast with helpful error
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env file")

# WRONG - Silent fallback to wrong value
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://roofio:pass@localhost/roofio")
```

### 3.5. Anti-Patterns to Avoid

| Anti-Pattern | Why | Do Instead |
|--------------|-----|------------|
| Hardcoded credential defaults | Auth failures, security risk | Empty string + validation |
| Relative imports in scripts | ImportError when run directly | Use asyncpg/raw SQL |
| Quick workarounds | User explicitly hates these | Fix root cause |
| Assuming .env is correct | Wastes debugging time | Validate and show errors |
| Multiple workarounds | Tech debt accumulates | One proper fix |

---

## 4. CAD Observer Protocol

### 4.1. Armand's Background

- 20+ year journeyman roofer/waterproofer
- Local 30 union member
- Teaches apprentices - values clear, teachable details
- Uses AutoCAD LT

### 4.2. Question-First Protocol

When Armand shares CAD screenshots, command logs, or asks you to observe his work:

1. **DESCRIBE** what you see factually (no interpretation)
2. **ASK 2-3 QUESTIONS** before logging:
   - "What spec section is this addressing?"
   - "Is this your standard approach or project-specific?"
   - "What problem are you solving here?"
3. **WAIT** for response
4. **THEN** log with confirmed intent

**NEVER assume intent. Wrong documentation is worse than no documentation.**

### 4.3. Specification Sections

| Code | Description |
|------|-------------|
| 07 62 00 | Sheet Metal Flashing and Trim |
| 07 50 00 | Membrane Roofing |
| 07 27 00 | Air Barriers |
| 07 92 00 | Joint Sealants |

### 4.4. Observation Logging Format

```json
{
  "timestamp": "ISO-8601",
  "project_context": "project name and drawing",
  "capture_metadata": {
    "click_x": 0,
    "click_y": 0,
    "mode": "cad|research"
  },
  "claude_observations": {
    "what_i_see": "factual description only",
    "commands_detected": [],
    "layer_patterns": [],
    "geometry_notes": []
  },
  "questions_asked": [
    {"question": "...", "user_response": "..."}
  ],
  "confirmed_intent": "Armand's stated purpose",
  "user_style_notes": "what Armand said about his approach",
  "tags": ["flashing", "detail", "standard"]
}
```

### 4.5. Scripts

```bash
# Click capture (CAD work)
python scripts/click_capture.py --project "Project Name"

# Research capture (specs/literature)
python scripts/research_capture.py --project "Project Name"

# All-in-one toolbar
python scripts/floating_toolbar.py --project "Project Name"
```

### 4.6. AutoCAD LISP Commands

Load `scripts/cad-observer.lsp` in AutoCAD:

| Command | Action |
|---------|--------|
| `CAD-OBSERVER-START` | Start logging session |
| `CAD-OBSERVER-STOP` | Stop logging session |
| `CAD-OBSERVER-STATUS` | Show current status |
| `CAD-OBSERVER-TASK` | Check for Claude tasks |
| `CAD-OBSERVER-AUTO` | Toggle auto-task execution |

### 4.7. Task System (Claude -> AutoCAD)

```bash
# Send AutoCAD commands
python scripts/cad_task.py script "ZOOM E" "LAYER M FLASH" "PLINE"

# Send LISP code
python scripts/cad_task.py lisp "(command \"CIRCLE\" \"0,0\" 5)"

# Query drawing state
python scripts/cad_task.py query
```

**Task Flow:**
1. Claude creates task file in `C:/CADObserver/tasks/`
2. AutoCAD LISP plugin detects and executes
3. Task moves to `C:/CADObserver/done/`
4. Results logged to `C:/CADObserver/logs/`

---

## 5. Decision Log (ADR Summary)

Key high-impact decisions that impact the architecture.

| ID | Decision | Status | Date |
|----|----------|--------|------|
| ADR-001 | Use `agency_id` for all multi-tenant tables | Accepted | 2025-12-13 |
| ADR-002 | Standalone init_db.py with asyncpg (no SQLAlchemy imports) | Accepted | 2025-12-13 |
| ADR-003 | Tiered AI: Python (95%) → Groq (4%) → Claude (1%) | Accepted | 2025-12-08 |
| ADR-004 | Upstash Redis + Vector for serverless infrastructure | Accepted | 2025-12-08 |
| ADR-005 | Custom form templates with scanner digitization | Accepted | 2025-12-12 |
| ADR-006 | No hardcoded credential defaults in config | Accepted | 2025-12-13 |

---

## 6. Permanent AI Skills (Always Active)

These skills are **always active** for every Claude Code session in this repository:

### Skill 1: Commit Curator
All proposed changes must adhere to the **Conventional Commits** standard:
- Structure output as small, logical commits
- Each commit = ONE logical unit of work
- Format: `type(scope): subject`
- Explain the "why" in descriptions

### Skill 2: Context Enforcer
Reference and adhere to Architectural Constraints:
- All tables use `agency_id` (never organization_id, company_id)
- NEVER hardcode credential defaults
- NEVER use relative imports in standalone scripts
- NO quick fixes - fix root causes only

### Skill 3: Mandatory Validation
Before every code suggestion:
1. Propose running appropriate test command
2. Ask for confirmation before code changes
3. Verify .env is correctly configured

### Skill 4: Documentation Guardian
After accepting changes, propose updates to:
- `CLAUDE.md` if architecture changed
- `SESSION-LOG.md` with problems/solutions
- `README.md` changelog for significant changes

---

## 7. Slash Commands

Available commands (type `/command-name` in Claude Code):

| Command | Purpose |
|---------|---------|
| `/best-practices` | Initialize Best Practice Mode with all skills |
| `/session-start` | Start session protocol - read context, check status |
| `/session-end` | End session protocol - update docs, commit, handoff |
| `/adr` | Create Architectural Decision Record |
| `/update-docs` | Propose documentation updates after changes |
| `/validate` | Run validation checks before code changes |

### Usage Examples

```bash
# Start of session
/session-start

# Before making architectural decision
/adr

# After completing feature/fix
/update-docs

# Before any code changes
/validate

# End of session
/session-end
```

---

## 8. Session Workflow

### 8.1. Starting a Session

1. Read `CLAUDE.md` (this file)
2. Read `SESSION-LOG.md` for recent context
3. Check `CLAUDE-INSTRUCTIONS.md` for current priorities
4. Ask clarifying questions before starting work

### 8.2. During a Session

1. Use TodoWrite to track tasks
2. Commit atomic changes with conventional commits
3. Test before proposing code
4. Document problems and solutions

### 8.3. Ending a Session

1. Update `SESSION-LOG.md` with:
   - What was done
   - Problems encountered and solutions
   - Learnings for next session
2. Update `CLAUDE-INSTRUCTIONS.md` with next priorities
3. Commit and push changes

---

## 9. Storage Locations

| Data | Location |
|------|----------|
| CAD captures | `~/.cad-observer/sessions/` |
| Research captures | `~/.cad-observer/research/` |
| Observation log | `~/.cad-observer/observations.jsonl` |
| Backend .env | `roofio-backend/.env` |
| Database schema | `roofio-backend/database/unified_schema.sql` |

---

## 10. Common Commands

```bash
# Run APPIO frontend
cd roofing_intelligence && python app.py

# Run Backend API
cd roofio-backend && uvicorn main:app --reload --port 8000

# Initialize database
cd roofio-backend && python init_db.py

# Test Redis connection
cd roofio-backend && python test_redis.py

# Test Groq AI
cd roofio-backend && python test_groq.py
```

---

## 11. Prediction Protocol

After 5+ confirmed observations:
- Begin making predictions: "Based on what you've told me..."
- Always ask "Did I get that right?" to track accuracy
- Never predict from unconfirmed observations

---

*Last updated by Claude on December 13, 2025*
