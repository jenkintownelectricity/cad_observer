# Session End Protocol

Ending the current Claude Code session. Execute the following wrap-up:

## Step 1: Update SESSION-LOG.md
Add entry with:
```markdown
## Session: YYYY-MM-DD - [Brief Title]

**Branch:** `branch-name`
**Duration:** ~X hours
**Outcome:** Success / Partial / Blocked

### What Was Done
- Bullet points of completed work

### What Changed (Files)
| File | Change Type | Description |
|------|-------------|-------------|

### Problems Encountered
1. **Problem:** Description
   - **Cause:** Root cause
   - **Solution:** What fixed it
   - **Learning:** What to remember

### What Worked Well
- Patterns that should be repeated

### What Didn't Work
- Approaches that failed and why

### Next Session Should
1. First priority
2. Second priority
```

## Step 2: Update CLAUDE-INSTRUCTIONS.md
Update the "Next Session Priorities" section with current state.

## Step 3: Update README.md Changelog
If significant changes were made, add changelog entry.

## Step 4: Commit Documentation
```bash
git add SESSION-LOG.md CLAUDE-INSTRUCTIONS.md README.md
git commit -m "docs(session): End session [date] - [brief summary]"
```

## Step 5: Git Status Check
```bash
git status
git log --oneline -3
```

## Step 6: Provide Handoff Summary
Summarize for the next session:
- What was accomplished
- What's pending
- Any blockers
- Recommended next steps

---

**Session wrap-up complete.**
