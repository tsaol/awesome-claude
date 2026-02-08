---
name: git-commit
description: Review project consistency and commit changes. Checks code vs docs alignment, updates CHANGELOG/README/DESIGN.md, updates ~/history.log, then commits and pushes. Use after finishing code modifications.
---

# Git Commit - Review, Fix & Commit

## Overview

This skill reviews project consistency after code changes to ensure:
- Code matches design documents
- CHANGELOG is updated for new features/fixes
- README reflects current functionality
- No outdated documentation
- ~/history.log is updated with session summary (if exists)

## When to Use

Trigger `/git-commit` after:
- Completing a feature implementation
- Fixing a bug
- Before creating a PR
- After significant code refactoring

## Review Checklist

### 1. Code vs Design Docs

Check if implementation matches design:
- Architecture follows design patterns
- API endpoints match specification
- Data models align with schema

```bash
# Find design docs
find . -name "DESIGN.md" -o -name "*.design.md" -o -name "design*.md"
```

### 2. CHANGELOG Update

Verify CHANGELOG.md includes:
- New features added
- Bugs fixed
- Breaking changes noted
- Version number updated (if applicable)

```bash
# Check recent changes vs CHANGELOG
git diff HEAD~5 --name-only
cat CHANGELOG.md | head -50
```

### 3. README Accuracy

Ensure README.md reflects:
- Current installation steps
- Updated usage examples
- New CLI commands/options
- Correct configuration

```bash
# Compare README with actual code
cat README.md
```

### 4. History Log Update

Check if `~/history.log` exists and update it with session summary:

```bash
# Check if history.log exists
if [ -f ~/history.log ]; then
    echo "history.log exists, will update"
fi
```

If exists, append a summary of changes made in this session:

```markdown
=== {DATE} {PROJECT_NAME} - {BRIEF_DESCRIPTION} ===

## Changes
- Feature/fix description
- Files modified
- PRs created

## Key Commands
- python hub/main.py search "query"
- etc.
```

### 5. Consistency Report

Generate a report:

```markdown
## Consistency Check Report

### Files Changed
- [ ] List modified files

### Documentation Status
- [ ] CHANGELOG updated: Yes/No
- [ ] README accurate: Yes/No
- [ ] Design docs aligned: Yes/No
- [ ] ~/history.log updated: Yes/No/Not exists

### Issues Found
- Issue 1: ...
- Issue 2: ...

### Recommendations
- Action 1: ...
- Action 2: ...
```

## Workflow

```
Code Changes Complete
        ↓
    /git-commit
        ↓
┌─────────────────────────┐
│ 1. Read changed files   │
│ 2. Check CHANGELOG      │
│ 3. Verify README        │
│ 4. Compare with docs    │
│ 5. Update ~/history.log │
│ 6. Generate report      │
│ 7. Fix issues (if any)  │
│ 8. Git commit & push    │
└─────────────────────────┘
```

## Auto Commit

After fixing all issues, automatically commit and push:

1. **Stage changes**: `git add` modified docs
2. **Commit**: Use descriptive message based on changes
3. **Push**: Push to remote branch
4. **Create PR**: If on feature branch, create PR with reviewer

```bash
# Example commit flow
git add CHANGELOG.md DESIGN.md README.md
git commit -m "docs: update documentation for recent changes"
git push origin <branch>
gh pr create --reviewer tsaol  # if on feature branch
```

**Commit message format**:
- `docs: update CHANGELOG for {feature}`
- `docs: sync README with current implementation`
- `docs: update DESIGN.md schema`

## Usage

```
/git-commit              # Full consistency review
/git-commit --quick      # Quick check (CHANGELOG + README only)
/git-commit --verbose    # Detailed report with suggestions
```

## Example Output

```
## Git Check Report

### Changed Files (last commit)
- src/storage.py
- src/main.py

### CHANGELOG Status
⚠️  CHANGELOG.md not updated for recent changes

### README Status
✅ README.md is up to date

### Recommendations
1. Add entry to CHANGELOG.md:
   - "fix: save url/source/category in sent_news.json"
```
