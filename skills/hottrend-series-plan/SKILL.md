---
name: hottrend-series-plan
description: Plan a series of hottrend articles. Interactive discussion to research topic, propose structure, and generate plan.md. Phase A of the series workflow. Requires the external ai-writing repo (AI_WRITING_DIR).
---

# Hottrend Series Plan - 系列热点文章规划

与用户交互式讨论，规划一个系列热点文章的拆分方案，最终生成 plan.md。

## Usage

```
/hottrend-series-plan <topic>
```

**Examples:**
```
/hottrend-series-plan "AI 截流 2026"
/hottrend-series-plan "大模型落地企业"
/hottrend-series-plan "开源 vs 闭源 LLM"
```

## Prerequisites（外部依赖）

本 skill 依赖外部仓库 **ai-writing**（包含 PROMPT 文件），本仓库不包含这些文件。通过环境变量 `AI_WRITING_DIR` 指定其位置，默认 `~/code/ai-writing`：

```bash
export AI_WRITING_DIR="$HOME/code/ai-writing"   # 按实际位置修改
```

**开始执行前先检查**，缺失时立即停止并清晰提示用户，不要凭空臆造流程：

```bash
AI_WRITING_DIR="${AI_WRITING_DIR:-$HOME/code/ai-writing}"
[ -f "$AI_WRITING_DIR/PROMPT-hottrend-series.md" ] || { echo "✗ 未找到 $AI_WRITING_DIR/PROMPT-hottrend-series.md：本 skill 需要外部 ai-writing 仓库，请 clone 后设置 AI_WRITING_DIR"; exit 1; }
```

## Execution

**执行此 skill 时，必须读取以下 PROMPT 文件，并执行「阶段 A: 系列规划」部分：**

```
$AI_WRITING_DIR/PROMPT-hottrend-series.md
```

### 流程概览

```
A1. 话题调研     → search_web.py 搜索，梳理子方向
A2. 提出系列方案  → 选择结构（递进/聚焦/角色式），拆分 N 篇
A3. 与用户讨论    → 迭代调整，直到用户满意
A4. 生成 plan.md → articles/series/<series-name>/plan.md
```

### 交互式过程

这是一个**对话式**的规划过程，不是一次性输出：

1. **调研** — 搜索话题，了解热点格局
2. **提案** — 向用户提出拆分方案（每篇的角度、受众、核心问题）
3. **讨论** — 用户可调整篇数、角度、受众等
4. **确认** — 用户满意后生成 plan.md

### 系列结构模式

| 结构 | 适用场景 | 示例 |
|------|---------|------|
| 递进式 | 新概念科普 | 是什么 → 为什么 → 怎么办 |
| 聚焦式 | 行业分析 | 宏观 → 中观 → 微观 |
| 角色式 | 争议话题 | 消费者 → 企业 → 平台 |

## Output

```
articles/series/<series-name>/
├── research/       # 调研资料
└── plan.md         # 系列计划（frontmatter + 各篇定义）
```

**plan.md 结构：**
```yaml
---
series: 系列中文名称
series_name: english-series-name
parts: N
status: planned
---
```

每篇包含: status, angle, audience, sources, hook, article_dir

## Next Step

plan.md 生成后，用户可逐篇生成：

```
/hottrend-series <series-name> 1
/hottrend-series <series-name> 2
...
```
