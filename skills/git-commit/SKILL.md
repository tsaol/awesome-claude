---
name: git-commit
description: Review project consistency and commit changes. Checks code vs docs alignment, updates CHANGELOG/README/DESIGN.md, updates ~/history.log, bumps version, then commits, pushes, and deploys if configured. Use after finishing code modifications.
---

# Git Commit - Review, Fix, Commit & Deploy

## Overview

This skill reviews project consistency after code changes to ensure:
- Code matches design documents
- CHANGELOG is updated for new features/fixes
- README reflects current functionality
- No outdated documentation
- ~/history.log is updated with session summary (if exists)
- Version number is bumped appropriately
- Deployment is triggered if configured in `~/.claude/collaboration.yml`

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

### 5. Version Bump

Automatically detect and bump the project version before committing.

**5a. Detect version file:**

```bash
# Check common version file locations (in priority order)
[ -f package.json ] && echo "package.json"
[ -f pyproject.toml ] && echo "pyproject.toml"
[ -f setup.py ] && echo "setup.py"
[ -f setup.cfg ] && echo "setup.cfg"
[ -f VERSION ] && echo "VERSION"
[ -f version.txt ] && echo "version.txt"
[ -f Cargo.toml ] && echo "Cargo.toml"
[ -f build.gradle ] && echo "build.gradle"
```

**5b. Determine bump type based on changes:**

| Change Type | Bump | Examples |
|-------------|------|----------|
| Bug fix, typo, minor tweak | **patch** (0.0.x) | fix query bug, update docs typo |
| New feature, enhancement | **minor** (0.x.0) | add user avatar upload, add new API endpoint |
| Breaking change, major rewrite | **major** (x.0.0) | change API response format, remove deprecated endpoints |

**Decision logic:**
1. Check git diff for breaking changes (removed public APIs, changed signatures, schema migrations)
2. Check if new files/modules were added (likely minor)
3. Default to **patch** if only modifications to existing files

**5c. Bump the version:**

```bash
# Python (pyproject.toml) - example: 0.2.1 → 0.2.2
# Read current version, calculate new version, update file
grep 'version = ' pyproject.toml

# Node.js (package.json) - example: 1.3.0 → 1.4.0
# Use npm version or manual edit
grep '"version"' package.json

# Plain VERSION file
cat VERSION
```

**5d. Update CHANGELOG with new version header:**

If CHANGELOG.md exists, ensure the new version appears at the top:

```markdown
## [0.2.2] - 2026-02-26

- Fix slow query in user search
- Update error handling for API timeout
```

**Important:**
- Always show the user the current version and proposed new version before bumping
- If no version file exists, skip this step and note it in the report
- Version bump changes are included in the same commit

### 6. Consistency Report

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

### Version
- [ ] Version file detected: Yes (package.json) / No
- [ ] Current version: 0.2.1
- [ ] Bump type: patch / minor / major
- [ ] New version: 0.2.2

### Deploy Config
- [ ] Deploy configured: Yes/No
- [ ] Method: ssm / ssh / script / N/A
- [ ] Target: instance-id or host

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
┌──────────────────────────────┐
│  1. Read changed files       │
│  2. Check CHANGELOG          │
│  3. Verify README            │
│  4. Compare with docs        │
│  5. Update ~/history.log     │
│  6. Version Bump             │
│  7. Generate report          │
│  8. Fix issues (if any)      │
│  9. Git commit & push        │
│ 10. Auto Deploy (if config)  │
└──────────────────────────────┘
```

## Auto Commit

After fixing all issues, automatically commit and push:

1. **Stage changes**: `git add` modified files
2. **Commit**: Summarize code changes in simple, human-like message
3. **Push**: Push to remote branch
4. **Create PR**: If on feature branch, create PR with reviewer

### Commit Message Style

**ALWAYS use simple, human-like commit messages:**

- Keep messages short and natural
- Summarize what the code changes actually do
- Use casual, everyday language
- Avoid formal conventions like "feat:", "chore:", "refactor:", etc.
- Write like a human developer would in daily work
- **Never include any Claude-related attribution**:
  - No "Generated with Claude Code"
  - No "Co-Authored-By: Claude"

**Good examples:**
- `add user login`
- `fix slow queries`
- `update packages`
- `add image download to browser fetcher`
- `store s3 paths in opensearch`

**Bad examples:**
- `feat: implement comprehensive user authentication system with JWT token validation`
- `chore: update dependencies to latest versions`
- `docs: update CHANGELOG for feature xyz`

```bash
# Example commit flow
git add .
git commit -m "add browser fetcher with screenshot support"
git push origin <branch>
gh pr create --reviewer tsaol  # if on feature branch
```

## Auto Deploy

After a successful push, check if the project has deployment configured and trigger it.

### Deploy Config

Deployment is configured per-project in `~/.claude/collaboration.yml`:

```yaml
projects:
  my-project:
    repo: user/my-project
    deploy:
      method: ssm           # Deployment method (ssm, ssh, script)
      instance: i-0abc123   # Target instance (for ssm/ssh)
      command: "cd /app && git pull origin main && sudo systemctl restart myapp"
```

### Supported Deploy Methods

| Method | Description | Required Fields |
|--------|-------------|-----------------|
| `ssm` | AWS Systems Manager Run Command | `instance`, `command` |
| `ssh` | SSH to remote server | `host`, `user`, `command` |
| `script` | Run a local script | `command` |

### Deploy Logic

**Step 1: Check if deploy is configured**

```bash
# Read collaboration.yml and find current project's deploy config
cat ~/.claude/collaboration.yml
```

Identify current project by matching `git remote -v` against the `repo` field in collaboration.yml.

**Step 2: Check if deploy should trigger**

Deploy ONLY when:
- Current branch is `main` or `master` (direct push workflow)
- OR a PR was just merged to main (github-flow workflow)
- The push was successful

Do NOT deploy when:
- On a feature branch (not yet merged)
- Push failed
- `--no-deploy` flag is used

**Step 3: Confirm with user**

```
🚀 Deploy detected for project "languages"
   Method: ssm
   Instance: i-0f86894d2231b1cd0
   Command: cd /home/ubuntu/languages && git pull origin main && sudo systemctl restart englearn

   Proceed with deployment? (y/n)
```

**Always ask for confirmation before deploying.** Never auto-deploy without user approval.

**Step 4: Execute deployment**

```bash
# SSM method
aws ssm send-command \
  --instance-ids "i-0abc123" \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"<deploy-command>\"]" \
  --output text

# SSH method
ssh user@host "<deploy-command>"

# Script method
bash -c "<deploy-command>"
```

**Step 5: Verify deployment**

```bash
# Check SSM command status
aws ssm list-command-invocations \
  --command-id "<command-id>" \
  --details \
  --output text

# Or check service status via SSM
aws ssm send-command \
  --instance-ids "i-0abc123" \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"systemctl status <service>\"]"
```

**Step 6: Report deploy result**

```markdown
### Deploy Result
- Project: languages
- Method: ssm
- Instance: i-0f86894d2231b1cd0
- Status: ✅ SUCCESS / ❌ FAILED
- Details: Service restarted successfully
```

## Usage

```
/git-commit              # Full consistency review + commit + deploy
/git-commit --quick      # Quick check (CHANGELOG + README only)
/git-commit --verbose    # Detailed report with suggestions
/git-commit --no-deploy  # Skip deployment even if configured
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
   - "save url/source/category in sent_news.json"
```
