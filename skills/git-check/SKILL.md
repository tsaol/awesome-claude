---
name: git-check
description: Review project consistency after code changes. Checks if code, design docs, CHANGELOG, and README are aligned. Use after finishing code modifications and before committing.
---

# Git Check - Project Consistency Review

## Overview

This skill reviews project consistency after code changes to ensure:
- Code matches design documents
- CHANGELOG is updated for new features/fixes
- README reflects current functionality
- No outdated documentation
- ~/history.log is updated with session summary (if exists)

## When to Use

Trigger `/git-check` after:
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
    /git-check
        ↓
┌─────────────────────────┐
│ 1. Read changed files   │
│ 2. Check CHANGELOG      │
│ 3. Verify README        │
│ 4. Compare with docs    │
│ 5. Update ~/history.log │
│ 6. Generate report      │
└─────────────────────────┘
        ↓
    Fix Issues (if any)
        ↓
    git commit
```

## Usage

```
/git-check              # Full consistency review
/git-check --quick      # Quick check (CHANGELOG + README only)
/git-check --verbose    # Detailed report with suggestions
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
