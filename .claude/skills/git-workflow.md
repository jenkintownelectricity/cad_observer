# Git Workflow Skill: VS Code + Claude Code (Web Browser)

> **CRITICAL**: Claude Code runs in a web browser. User runs VS Code locally. These environments are NOT synced.

---

## The Setup

| Environment | Git Access | Can Push/Pull | Notes |
|-------------|-----------|---------------|-------|
| **Claude Code** | Yes (web browser) | Yes, to feature branches | Cannot push directly to main |
| **User's VS Code** | Yes (local machine) | Yes, to any branch | Has full git control |

**Key Understanding**: Claude Code works on a feature branch. User merges to main locally.

---

## After Completing Major Work

When Claude Code finishes a significant piece of work, provide these commands for the user to run in VS Code terminal:

### Standard Merge Flow (Copy-Paste for User)

```bash
# 1. Fetch the latest changes from Claude's branch
git fetch origin claude/[branch-name]

# 2. Checkout main and ensure it's up to date
git checkout main
git pull origin main

# 3. Merge Claude's branch into main
git merge origin/claude/[branch-name]

# 4. Push merged main to remote
git push origin main

# 5. Delete the feature branch (optional cleanup)
git branch -d claude/[branch-name]
git push origin --delete claude/[branch-name]
```

### Quick One-Liner (for experienced users)

```bash
git fetch origin && git checkout main && git pull && git merge origin/claude/[branch-name] && git push && git branch -d claude/[branch-name] && git push origin --delete claude/[branch-name]
```

---

## What Claude Code Should Do

1. **Always commit work** to the feature branch before giving instructions
2. **Always push** to the feature branch so user can fetch it
3. **Never assume** the user has the latest changes locally
4. **Provide exact commands** with the actual branch name filled in
5. **Remind user** they need to run these in VS Code, not here

---

## What Claude Code Should NOT Do

1. **Never push to main** - Claude Code cannot do this
2. **Never assume git sync** - The environments are separate
3. **Never say "just merge"** - Give exact commands
4. **Never forget** to push before giving merge instructions

---

## Current Branch Template

When finishing work, say:

```
## Ready to Merge

I've pushed all changes to: `claude/[actual-branch-name]`

**Run these commands in your VS Code terminal:**

\`\`\`bash
git fetch origin claude/[actual-branch-name]
git checkout main
git pull origin main
git merge origin/claude/[actual-branch-name]
git push origin main
git push origin --delete claude/[actual-branch-name]
\`\`\`

After running these, your main branch will have all the changes.
```

---

## Handling Merge Conflicts

If user reports merge conflicts, provide:

```bash
# View conflicting files
git status

# After manually resolving conflicts in VS Code:
git add .
git commit -m "Resolve merge conflicts from claude/[branch-name]"
git push origin main
```

---

## Testing Locally

Remind user they can test before merging:

```bash
# Test on Claude's branch first
git fetch origin claude/[branch-name]
git checkout claude/[branch-name]

# Run your tests/server here

# If everything works, merge to main
git checkout main
git merge claude/[branch-name]
git push origin main
```

---

## Remember

1. **Claude Code = Web Browser** (isolated environment)
2. **User = VS Code** (local machine with full control)
3. **Always push** before giving merge instructions
4. **Always provide** copy-paste commands
5. **Never assume** environments are synced

---

*Skill created December 12, 2025*
