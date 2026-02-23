---
name: git-review
description: Review code changes against requirements and original design. Validates implementation correctness, design alignment, code quality, and runs tests. Use before committing or creating a PR.
---

# Git Review - Requirements Check, Design Validation & Testing

## Overview

This skill performs a thorough code review by:
- Verifying code changes match the stated requirements (issue, PR description, or user input)
- Checking changes are sensible modifications aligned with the original design
- Evaluating code quality, patterns, and potential issues
- Running project tests to ensure nothing is broken

## When to Use

Trigger `/git-review` when:
- You've finished implementing a feature and want to verify before committing
- You want to validate code changes against an issue or PR description
- You need a sanity check that changes align with the project's architecture
- Before running `/git-commit` to ensure quality

## Usage

```
/git-review                      # Review all uncommitted changes
/git-review <issue-url>          # Review changes against a GitHub issue
/git-review <pr-url>             # Review an existing PR
/git-review --design-only        # Skip tests, only check design alignment
/git-review --test-only          # Only run tests
```

### Flag behavior

- **No flags**: Run all 6 phases
- **`--design-only`**: Run Phase 1 (context) → Phase 2 (requirements) → Phase 3 (design) → Phase 4 (code quality) → Phase 6 (report). Skip Phase 5 (tests).
- **`--test-only`**: Run Phase 1 (context) → Phase 5 (tests) → Phase 6 (report). Skip Phase 2-4.

## Workflow

```
Code Changes Ready
        |
    /git-review
        |
+----------------------------------+
| Phase 1: Gather Context          |
|   - Collect uncommitted changes  |
|   - Read requirements source     |
|   - Read design docs             |
+----------------------------------+
        |
+----------------------------------+
| Phase 2: Requirements Check      |
|   - Map changes to requirements  |
|   - Flag missing implementations |
|   - Flag scope creep             |
+----------------------------------+
        |
+----------------------------------+
| Phase 3: Design Alignment        |
|   - Check architecture fit       |
|   - Validate patterns & naming   |
|   - Review data model changes    |
+----------------------------------+
        |
+----------------------------------+
| Phase 4: Code Quality            |
|   - Logic correctness            |
|   - Error handling               |
|   - Security considerations      |
|   - Edge cases                   |
+----------------------------------+
        |
+----------------------------------+
| Phase 5: Run Tests               |
|   - Detect test framework        |
|   - Run existing tests           |
|   - Report failures              |
+----------------------------------+
        |
+----------------------------------+
| Phase 6: Review Report           |
|   - Summary with verdict         |
|   - Issues & recommendations     |
|   - Suggested fixes              |
+----------------------------------+
```

## Phase Details

### Phase 1: Gather Context

Collect all information needed for the review.

**1a. Collect code changes:**

```bash
# Uncommitted changes (staged + unstaged)
git diff HEAD

# If no uncommitted changes, review last commit only
git show HEAD --stat
git diff HEAD~1 HEAD

# List changed files
git diff HEAD --name-only
```

**1b. Identify requirements source:**

Requirements can come from:
- **GitHub Issue**: Extract from issue URL via `gh issue view <number>`
- **GitHub PR**: Extract from PR description via `gh pr view <number>`
- **User input**: The user describes what the changes should do
- **Commit messages**: Infer intent from recent commit messages

```bash
# If a GitHub issue/PR URL is provided
gh issue view <number> --json title,body,labels
gh pr view <number> --json title,body,commits,files

# Recent commit messages for context
git log --oneline -10
```

**1c. Find design documents:**

```bash
# Look for design docs in the project
find . -maxdepth 3 \( \
  -name "DESIGN.md" -o \
  -name "ARCHITECTURE.md" -o \
  -name "*.design.md" -o \
  -name "design*.md" -o \
  -name "SPEC.md" -o \
  -name "spec*.md" -o \
  -name "RFC*.md" -o \
  -name "ADR*.md" \
\) -not -path "*/node_modules/*" -not -path "*/.git/*"

# Also check for inline design comments in changed files
```

### Phase 2: Requirements Check

Compare the code changes against stated requirements.

**Checklist:**

- [ ] **Completeness**: Every requirement has a corresponding code change
- [ ] **No missing pieces**: All acceptance criteria are addressed
- [ ] **No scope creep**: Changes don't include unrelated modifications
- [ ] **Edge cases**: Requirements' edge cases are handled

**How to check:**

1. Parse the requirements into a bullet list of expected behaviors
2. For each requirement, identify the code that implements it
3. Flag any requirement without matching code (missing implementation)
4. Flag any code change that doesn't map to a requirement (scope creep)

### Phase 3: Design Alignment

Verify changes respect the project's existing architecture and design.

**Checklist:**

- [ ] **Architecture fit**: New code follows the project's module structure
- [ ] **Design patterns**: Uses the same patterns as existing code (e.g., if the project uses repository pattern, new data access follows it)
- [ ] **Naming conventions**: Variables, functions, files follow project conventions
- [ ] **Data model consistency**: Schema changes are backward-compatible or properly migrated
- [ ] **API contract**: Endpoint changes maintain backward compatibility or are versioned
- [ ] **Dependency direction**: No circular dependencies introduced
- [ ] **Separation of concerns**: Business logic not mixed with presentation/infrastructure

**How to check:**

1. Read DESIGN.md / ARCHITECTURE.md if they exist
2. **If no design docs exist**: Infer the design by examining existing code structure, module organization, import patterns, and naming conventions in the same directory/module
3. Examine the structure of unchanged files in the same module
4. Compare new code patterns against existing patterns in the project
5. Verify imports and dependencies flow in the correct direction

### Phase 4: Code Quality

Review the actual code for correctness and quality.

**Checklist:**

- [ ] **Logic correctness**: Algorithms and conditions are correct
- [ ] **Error handling**: Errors are caught and handled appropriately, not swallowed
- [ ] **Security**: No injection vulnerabilities, secrets not hardcoded, inputs validated at boundaries
- [ ] **Edge cases**: Null/empty/boundary values handled
- [ ] **Resource management**: Files, connections, streams are properly closed
- [ ] **Concurrency**: Thread safety if applicable
- [ ] **Performance**: No obvious N+1 queries, unnecessary loops, or memory leaks
- [ ] **Readability**: Code is clear without excessive complexity
- [ ] **TODO/FIXME/HACK**: Flag any leftover debug code, TODO comments, or HACK markers in changed files

**Severity levels:**

- **CRITICAL**: Bugs, security vulnerabilities, data loss risks
- **WARNING**: Code smells, potential issues, missing error handling
- **SUGGESTION**: Style improvements, minor optimizations

### Phase 5: Run Tests

Detect and run the project's test suite.

**Test framework detection:**

```bash
# Python
[ -f pytest.ini ] && echo "pytest"
[ -f setup.cfg ] && grep -q "\[tool:pytest\]" setup.cfg && echo "pytest"
[ -f pyproject.toml ] && grep -q "\[tool.pytest" pyproject.toml && echo "pytest"
[ -d tests ] || [ -d test ] && echo "pytest (test dir found)"
[ -f tox.ini ] && echo "tox"

# JavaScript/TypeScript
grep -q '"test"' package.json 2>/dev/null && echo "npm test"
grep -q '"vitest"' package.json 2>/dev/null && echo "vitest"
grep -q '"jest"' package.json 2>/dev/null && echo "jest"

# Go
[ -f go.mod ] && echo "go test"

# Rust
[ -f Cargo.toml ] && echo "cargo test"

# Java/Kotlin
[ -f pom.xml ] && echo "maven"
[ -f build.gradle ] || [ -f build.gradle.kts ] && echo "gradle"

# Generic
[ -f Makefile ] && grep -q "test" Makefile && echo "make test"
```

**Run tests:**

```bash
# Run with appropriate framework (examples)
pytest -v --tb=short 2>&1 | tail -50
npm test 2>&1 | tail -50
go test ./... 2>&1 | tail -50
cargo test 2>&1 | tail -50
```

**If no tests exist:**
- Note this in the report
- Suggest which tests should be written for the changed code

### Phase 6: Review Report

Generate a structured review report.

```markdown
## Git Review Report

### Requirements: [Issue/PR title or description]

### Verdict: PASS / PASS WITH WARNINGS / FAIL

---

### 1. Requirements Coverage

| Requirement | Status | Code Location |
|------------|--------|---------------|
| Feature A  | DONE   | src/foo.py:42 |
| Feature B  | MISSING | -            |

**Missing implementations:**
- [ ] Feature B: not found in changed files

**Scope creep:**
- (none, or list unrelated changes)

---

### 2. Design Alignment

| Check | Status | Notes |
|-------|--------|-------|
| Architecture fit | PASS | Follows existing module structure |
| Naming conventions | PASS | Consistent with project style |
| API compatibility | WARNING | Endpoint X changed signature |

**Issues:**
- WARNING: `GET /api/users` now requires `page` param (breaking change)

---

### 3. Code Quality

| File | Line | Severity | Issue |
|------|------|----------|-------|
| src/handler.py | 55 | CRITICAL | SQL injection via string formatting |
| src/utils.py | 12 | WARNING | Exception silently caught |
| src/model.py | 30 | SUGGESTION | Could use dataclass |

---

### 4. Test Results

**Framework**: pytest
**Result**: 42 passed, 1 failed, 0 errors

**Failures:**
- `test_user_creation`: AssertionError - expected 201, got 400

**Missing test coverage:**
- [ ] No tests for new endpoint `POST /api/orders`

---

### 5. Summary & Recommendations

**Must fix before commit:**
1. Fix SQL injection in src/handler.py:55
2. Add missing implementation for Feature B

**Should fix:**
1. Handle breaking API change (add versioning or migration)
2. Fix failing test `test_user_creation`

**Nice to have:**
1. Add tests for new endpoint
```

## Verdict Criteria

- **PASS**: All requirements met, no critical issues, tests pass
- **PASS WITH WARNINGS**: All requirements met, no critical issues, but has warnings or minor test failures
- **FAIL**: Missing requirements, critical issues found, or major test failures

## Integration with /git-commit

Typical workflow:

```
1. Write code
2. /git-review              # Check everything
3. Fix issues (if any)
4. /git-review              # Re-check
5. /git-commit              # Commit when review passes
```

## Example Output

```
## Git Review Report

### Requirements: Add user avatar upload (Issue #42)

### Verdict: PASS WITH WARNINGS

---

### 1. Requirements Coverage
| Requirement | Status | Code Location |
|------------|--------|---------------|
| Upload avatar image | DONE | src/api/avatar.py:15 |
| Validate file type (jpg/png) | DONE | src/api/avatar.py:28 |
| Resize to 200x200 | DONE | src/services/image.py:10 |
| Store in S3 | DONE | src/services/storage.py:45 |
| Update user profile | DONE | src/models/user.py:62 |

### 2. Design Alignment
| Check | Status |
|-------|--------|
| Architecture fit | PASS |
| Naming conventions | PASS |
| API compatibility | PASS |

### 3. Code Quality
| File | Line | Severity | Issue |
|------|------|----------|-------|
| src/api/avatar.py | 32 | WARNING | Max file size not enforced |

### 4. Test Results
**Framework**: pytest
**Result**: 58 passed, 0 failed

**Missing test coverage:**
- [ ] No test for oversized file upload

### 5. Summary
**Should fix:**
1. Add max file size validation (recommend 5MB)

**Nice to have:**
1. Add test for oversized file rejection
```
