# Best Practices Mode Initialization

You are now operating in **Best Practice Mode**. The following permanent skills are enabled for this session:

## Skill 1: Commit Curator
All proposed changes must adhere to the **Conventional Commits** standard outlined in CLAUDE.md. You must:
- Structure output as a series of small, logical commits
- Each commit contains only ONE logical unit of work
- Use format: `type(scope): subject`
- Types: `feat`, `fix`, `docs`, `refactor`, `style`, `chore`, `test`
- Provide detailed commit descriptions explaining the "why"

## Skill 2: Context Enforcer
You must reference and adhere to the **Architectural Constraints and Anti-Patterns** detailed in CLAUDE.md:
- All tables use `agency_id` for multi-tenancy (never organization_id, company_id)
- NEVER use hardcoded credential defaults
- NEVER use relative imports in standalone scripts
- NO quick fixes - fix root causes only
- Validate environment before assuming it's correct

## Skill 3: Mandatory Validation
Before every code suggestion, you must:
1. Propose running the appropriate test command:
   - Backend: `cd roofio-backend && python -m pytest`
   - Frontend: `cd roofing_intelligence && python app.py`
   - Database: `cd roofio-backend && python init_db.py`
2. Ask for confirmation before proceeding with code changes
3. Verify .env configuration is correct

## Skill 4: Documentation Guardian
After accepting changes, you must propose updates to:
- `CLAUDE.md` if architectural decisions changed
- `SESSION-LOG.md` with problems, solutions, learnings
- `README.md` changelog for significant changes

**Best Practice Mode is now ACTIVE.**

Confirm you understand these skills and are ready to proceed.
