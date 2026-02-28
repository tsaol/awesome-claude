---
name: product-review
description: Product review from a PM perspective. Uses multi-agent pipeline to analyze any project/codebase for product discovery, goal alignment, UX/DX audit, competitive analysis, and roadmap planning.
---

# Product Review - 多 Agent 产品经理评审

以产品经理视角全面评审任意项目/代码库，输出结构化评审报告和改进路线图。

## Usage

```
/product-review <project_path> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--quick` | Quick mode (skip competitive analysis, simplified roadmap) | false |
| `--focus=<area>` | Focus area: ux / dx / growth / tech | all |
| `--lang=<zh\|en>` | Output language | zh |

**Examples:**
```
/product-review .
/product-review ~/codes/my-project
/product-review . --quick
/product-review . --focus=ux --lang=en
/product-review ~/codes/my-project --quick --focus=dx
```

## Output Structure

All outputs are generated in the target project's root directory:

```
.product-review/
├── raw/snapshot.md                   # Phase 0: project snapshot
├── analysis/
│   ├── discovery.md                  # Agent 1 output
│   ├── goal-alignment.md             # Agent 2 output
│   ├── ux-dx-audit.md                # Agent 3 output
│   └── competitive-analysis.md       # Agent 4 output (Full mode only)
├── output/
│   └── pm-review.md                  # Final review report
└── process/
    └── pipeline.log                  # Execution log
```

## Pipeline

### Full Mode (5 Agents)

```
Phase 0: Project Snapshot (bash, no LLM)
    ↓ raw/snapshot.md
Agent 1: pr-discovery (Product Discovery)
    ↓ analysis/discovery.md
Agent 2: pr-goal-alignment  ←──┐ Parallel
Agent 3: pr-ux-dx-audit     ←──┘
    ↓ analysis/goal-alignment.md + analysis/ux-dx-audit.md
Agent 4: pr-competitive-analysis
    ↓ analysis/competitive-analysis.md
Agent 5: pr-roadmap-planner (Synthesize all)
    ↓ output/pm-review.md
```

### Quick Mode (3 Agents, skip Agent 4)

```
Phase 0 → Agent 1 → Agent 2 + Agent 3 (parallel) → Agent 5
```

## Execution Steps

### Step 0: Setup

```bash
PROJECT_PATH="<user_provided_path>"
cd "$PROJECT_PATH"
mkdir -p .product-review/{raw,analysis,output,process}
```

### Step 1: Phase 0 - Project Snapshot

Non-LLM step. Collect project metadata using bash commands and write to `.product-review/raw/snapshot.md`.

**Collect the following:**

```bash
# 1. README content
cat README.md 2>/dev/null || echo "No README.md found"

# 2. Directory structure (2 levels deep)
find . -maxdepth 2 -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/vendor/*' -not -path '*/__pycache__/*' -not -path '*/dist/*' -not -path '*/build/*' | head -100

# 3. Config files
for f in package.json pyproject.toml Cargo.toml go.mod composer.json Gemfile pom.xml build.gradle; do
  [ -f "$f" ] && echo "=== $f ===" && cat "$f"
done

# 4. Git log (last 20 commits)
git log --oneline -20 2>/dev/null || echo "Not a git repo"

# 5. GitHub stats (if remote exists)
REMOTE=$(git remote get-url origin 2>/dev/null)
if [ -n "$REMOTE" ]; then
  REPO=$(echo "$REMOTE" | sed 's/.*github.com[:/]\(.*\)\.git/\1/' | sed 's/.*github.com[:/]\(.*\)/\1/')
  gh api "repos/$REPO" --jq '{stars: .stargazers_count, forks: .forks_count, open_issues: .open_issues_count, language: .language, license: .license.spdx_id, created: .created_at, updated: .pushed_at}' 2>/dev/null
  gh api "repos/$REPO/pulls?state=open&per_page=1" --jq 'length' 2>/dev/null
fi

# 6. File type statistics
find . -type f -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/vendor/*' | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20
```

**Write to** `.product-review/raw/snapshot.md`:

```markdown
# Project Snapshot: {project_name}

> Generated: {timestamp}

## README
{readme_content}

## Directory Structure
{tree_output}

## Config Files
{config_content}

## Git History (Last 20 Commits)
{git_log}

## GitHub Stats
{github_stats}

## File Type Statistics
{file_stats}
```

**Log:**
```
[HH:MM] phase-0    | ✓ snapshot collected | → raw/snapshot.md
```

### Step 2: Agent 1 - Product Discovery

Run the `pr-discovery` agent.

**Input:** Read `.product-review/raw/snapshot.md`
**Output:** Agent writes to `.product-review/analysis/discovery.md`

```
[HH:MM] pr-discovery | ▶ started | raw/snapshot.md → analysis/discovery.md
[HH:MM] pr-discovery | ✓ done    | analysis/discovery.md
```

### Step 3: Agent 2 + Agent 3 (Parallel)

Run `pr-goal-alignment` and `pr-ux-dx-audit` **in parallel** using two Task tool calls in a single message.

**Agent 2 Input:** `.product-review/raw/snapshot.md` + `.product-review/analysis/discovery.md`
**Agent 2 Output:** `.product-review/analysis/goal-alignment.md`

**Agent 3 Input:** `.product-review/raw/snapshot.md` + `.product-review/analysis/discovery.md`
**Agent 3 Output:** `.product-review/analysis/ux-dx-audit.md`

```
[HH:MM] pr-goal-alignment | ▶ started | snapshot.md + discovery.md → goal-alignment.md
[HH:MM] pr-ux-dx-audit    | ▶ started | snapshot.md + discovery.md → ux-dx-audit.md
[HH:MM] pr-goal-alignment | ✓ done    | analysis/goal-alignment.md
[HH:MM] pr-ux-dx-audit    | ✓ done    | analysis/ux-dx-audit.md
```

### Step 4: Agent 4 - Competitive Analysis (Full Mode Only)

**Skip this step if `--quick` is set.**

Run the `pr-competitive-analysis` agent.

**Input:** `.product-review/raw/snapshot.md` + `.product-review/analysis/discovery.md`
**Output:** `.product-review/analysis/competitive-analysis.md`

```
[HH:MM] pr-competitive-analysis | ▶ started | snapshot.md + discovery.md → competitive-analysis.md
[HH:MM] pr-competitive-analysis | ✓ done    | analysis/competitive-analysis.md
```

### Step 5: Agent 5 - Roadmap Planner (Final Report)

Run the `pr-roadmap-planner` agent.

**Input:** All files in `.product-review/analysis/` + `.product-review/raw/snapshot.md`
**Output:** `.product-review/output/pm-review.md`

```
[HH:MM] pr-roadmap-planner | ▶ started | analysis/*.md → output/pm-review.md
[HH:MM] pr-roadmap-planner | ✓ done    | output/pm-review.md
```

### Step 6: Summary

After all agents complete, print:

```
✅ Product review complete!

📄 Report: .product-review/output/pm-review.md
📊 Analysis files: .product-review/analysis/
📋 Log: .product-review/process/pipeline.log
```

## Focus Mode Behavior

When `--focus=<area>` is set, agents should weight their analysis accordingly:

| Focus | Agent Emphasis |
|-------|---------------|
| `ux` | Agent 3 deep-dives into user experience, UI flows, error messages |
| `dx` | Agent 3 deep-dives into developer experience, API design, docs, SDK |
| `growth` | Agent 1 emphasizes growth potential, Agent 4 emphasizes market opportunity |
| `tech` | Agent 2 emphasizes technical implementation quality, architecture |

Pass the focus area to each agent via a note at the top of the snapshot:

```markdown
> **Review Focus:** {focus_area}
```

## Language Behavior

When `--lang=en` is set, all agents output in English. Default is Chinese (zh).

Pass the language preference to each agent via a note at the top of the snapshot:

```markdown
> **Output Language:** {zh|en}
```

## Log Format

All pipeline logs are appended to `.product-review/process/pipeline.log`:

```
[HH:MM] agent-name | status | description
```

Status symbols:
- `▶` started
- `✓` done
- `⚠` warning
- `✗` failed

## Final Report Template

The final report (`output/pm-review.md`) follows this template:

```markdown
# 产品评审报告: {project_name}

> 评审时间: {timestamp}
> 评审模式: Full / Quick
> 聚焦领域: {focus_area or "全面评审"}

## 执行摘要
> [1 段话核心结论]

## 评分卡
| 维度 | 得分 | 说明 |
|------|------|------|
| 产品力 | /10 | |
| 用户体验 | /10 | |
| 目标对齐 | /10 | |
| 竞争力 | /10 | |
| **综合** | **/10** | |

## 产品发现
[来自 Agent 1: pr-discovery]

## 目标对齐分析
[来自 Agent 2: pr-goal-alignment]

## 体验审计
[来自 Agent 3: pr-ux-dx-audit]

## 竞品分析
[来自 Agent 4: pr-competitive-analysis，Quick 模式标注"已跳过"]

## 改进路线图
### 🔴 立即修复 (P0, 1-2 周)
### 🟡 短期改进 (P1, 1-3 个月)
### 🟢 长期演进 (P2, 3-6 个月)

## 里程碑
| 阶段 | 目标 | 关键交付物 | 预计周期 |
|------|------|-----------|---------|
| M1 | | | 2 周 |
| M2 | | | 1-3 月 |
| M3 | | | 3-6 月 |

## 关键指标
- **北极星指标**: [建议的核心指标]
- **辅助指标**: [2-3 个辅助指标]
```
