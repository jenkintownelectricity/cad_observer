# ROOFIO File Audit Report

**Date:** December 2025
**Purpose:** Identify files for deletion and sync issues
**Status:** Awaiting Armand's Approval

---

## CRITICAL FINDING: Navigation Mismatch

The main navigation includes: **Dashboard, Analysis, Roofio, Projects, Phone**

But these important pages are NOT in the main nav:
- `/control-center` - ROOFIO Control Center (8 positions, AI modes)
- `/digital-foreman` - Digital Foreman (Risk Shield)
- `/integrations` - Integrations Hub (28+ connectors)

**RECOMMENDATION:** Add these to main navigation or create a clear entry point.

---

## FILES BY STATUS

### KEEP - Core Application (Active)

| File | Purpose | Status |
|------|---------|--------|
| `roofing_intelligence/app.py` | Main Flask application | Active |
| `roofing_intelligence/templates/dashboard.html` | Company dashboard | Active |
| `roofing_intelligence/templates/control_center.html` | 8 positions + AI modes | Active |
| `roofing_intelligence/templates/digital_foreman.html` | Risk Shield field app | Active |
| `roofing_intelligence/templates/integrations.html` | 28+ connectors | Active |
| `roofing_intelligence/templates/roofio.html` | Roofio AI chat | Active |
| `roofing_intelligence/templates/index.html` | Document analysis | Active |
| `roofing_intelligence/templates/inspector.html` | Guest inspector mode | Active |
| `roofing_intelligence/templates/projects.html` | Project management | Active |
| `roofing_intelligence/templates/phone.html` | Phone (coming soon) | Active |

### KEEP - Core Parsers (Active)

| File | Purpose | Status |
|------|---------|--------|
| `roofing_intelligence/parsers/arch_drawing_parser.py` | Drawing analysis | Active |
| `roofing_intelligence/parsers/assembly_parser.py` | Assembly letters | Active |
| `roofing_intelligence/parsers/pdf_extractor.py` | PDF text extraction | Active |
| `roofing_intelligence/parsers/roof_page_filter.py` | Smart page filtering | Active |
| `roofing_intelligence/parsers/scope_parser.py` | Scope of work | Active |
| `roofing_intelligence/parsers/spec_parser.py` | Specification parsing | Active |
| `roofing_intelligence/parsers/text_cleaner.py` | Text utilities | Active |

### KEEP - Platform Architecture (Reference)

| File | Purpose | Status |
|------|---------|--------|
| `roofing_intelligence/roofio/platform/schema.sql` | Main database schema | Reference |
| `roofing_intelligence/roofio/platform/digital_foreman/schema.sql` | Risk Shield schema | Reference |
| `roofing_intelligence/roofio/platform/digital_foreman/__init__.py` | Python services | Reference |
| `roofing_intelligence/roofio/platform/digital_foreman/api/routes.py` | API endpoints | Reference |
| `roofing_intelligence/roofio/platform/ROOFIO-PLATFORM-SPEC-v2.md` | UPO architecture | Reference |
| `roofing_intelligence/roofio/platform/INTEGRATION-HUB-SPEC.md` | Trojan Horse strategy | Reference |

### KEEP - Skills Documentation (Knowledge Base)

| File | Purpose | Status |
|------|---------|--------|
| `roofing_intelligence/roofio/skills/*/SKILL.md` | 14 skill documents | Keep All |
| `roofing_intelligence/roofio/groq_client.py` | Groq AI integration | Active |
| `roofing_intelligence/architect_ai/rules_engine.py` | AI routing logic | Active |

### KEEP - Documentation

| File | Purpose | Status |
|------|---------|--------|
| `CLAUDE.md` | Claude Code context | Keep |
| `NEXT-SESSION-BACKEND-MASTERPLAN.md` | Backend implementation guide | Keep |
| `roofing_intelligence/roofio/MANIFEST.md` | Roofio manifest | Keep |
| `roofing_intelligence/roofio/PARTNERSHIP-PACKAGE.md` | Partnership docs | Keep |

---

## CANDIDATES FOR DELETION

### 1. DUPLICATE - Old Session Document
| File | Reason |
|------|--------|
| `CLAUDE_SESSION.md` | Replaced by `NEXT-SESSION-BACKEND-MASTERPLAN.md` |

### 2. GENERATED HTML - Site Generator Output (48 files)
| Files | Reason |
|-------|--------|
| `roofing_intelligence/roofio/site-generator/build/*.html` | Auto-generated from Division 07 specs. Can regenerate. Takes up space. |

**List of 48 generated files:**
- 07-01-00-operation-and-maintenance-of-thermal-and-moisture-protection.html
- 07-05-00-common-work-results-for-thermal-and-moisture-protection.html
- 07-10-00-dampproofing-and-waterproofing.html
- ... (46 more)

### 3. DUPLICATE SCRIPTS - Root vs roofing_intelligence
| File | Reason |
|------|--------|
| `scripts/roof_page_filter.py` | Duplicate of `roofing_intelligence/parsers/roof_page_filter.py` |

### 4. PLACEHOLDER/EMPTY FILES
| File | Reason |
|------|--------|
| `roofing_intelligence/roofio/platform/badges/__init__.py` | Empty placeholder |
| `roofing_intelligence/roofio/platform/confidence/__init__.py` | Empty placeholder |
| `roofing_intelligence/roofio/platform/forms/__init__.py` | Empty placeholder |
| `roofing_intelligence/roofio/platform/positions/__init__.py` | Empty placeholder |

### 5. CAD OBSERVER SCRIPTS - Not used in ROOFIO
| File | Reason |
|------|--------|
| `scripts/cad_task.py` | CAD Observer functionality |
| `scripts/capture_session.py` | CAD Observer functionality |
| `scripts/click_capture.py` | CAD Observer functionality |
| `scripts/floating_toolbar.py` | CAD Observer functionality |
| `scripts/log_observation.py` | CAD Observer functionality |
| `scripts/research_capture.py` | CAD Observer functionality |
| `scripts/unified_session.py` | CAD Observer functionality |

**NOTE:** These are for the original CAD Observer project. Keep if you plan to use CAD observation features. Delete if ROOFIO is standalone.

### 6. STANDALONE HTML (Not in Flask app)
| File | Reason |
|------|--------|
| `roofing_intelligence/roofio/roofio-pitch.html` | Marketing page, not served by app |
| `roofing_intelligence/roofio/roofio-spec-index.html` | Spec index, not served by app |

---

## SUMMARY FOR APPROVAL

### Definitely Delete (Safe)
1. `CLAUDE_SESSION.md` - Replaced

### Recommend Delete (Clean Up)
2. 48 generated HTML files in `site-generator/build/` - Can regenerate
3. 4 empty `__init__.py` placeholder files - Not used
4. 1 duplicate script (`scripts/roof_page_filter.py`)

### Your Decision Required
5. 7 CAD Observer scripts - Keep if you want CAD integration, delete if ROOFIO is standalone
6. 2 standalone HTML files - Keep if you want marketing pages, delete if not needed

---

## TOTAL COUNTS

| Category | Count |
|----------|-------|
| Files to KEEP | 45+ |
| Definitely Delete | 1 |
| Recommend Delete | 53 |
| Your Decision | 9 |
| **Total Audit** | **108 files** |

---

## WAITING FOR YOUR APPROVAL

Reply with which categories to delete:
1. `yes` - Delete all recommended + CLAUDE_SESSION.md
2. `yes-all` - Delete everything including CAD scripts and marketing HTML
3. `keep-cad` - Delete recommended but keep CAD Observer scripts
4. `list` - Show me the exact files before deleting
