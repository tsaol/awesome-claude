---
name: hottrend-series
description: Generate a single article in a hottrend series. Reads plan.md, creates context, runs full hottrend pipeline with series context injection. Phase B of series workflow.
---

# Hottrend Series - 系列文章单篇生成

根据已有的 plan.md，生成系列中的指定一篇文章。复用完整 hottrend pipeline，注入系列上下文。

## Usage

```
/hottrend-series <series-name> <part-number> [extra-urls...]
```

**Examples:**
```
/hottrend-series ai-interception-2026 1
/hottrend-series ai-interception-2026 2 https://example.com/article1
/hottrend-series open-source-llm 3
```

## Prerequisites

必须先通过 `/hottrend-series-plan` 生成 plan.md：

```
articles/series/<series-name>/plan.md
```

如果 plan.md 不存在，提示用户先运行 `/hottrend-series-plan <topic>`。

## Execution

**执行此 skill 时，必须读取以下 PROMPT 文件，并执行「阶段 B: 单篇生成」部分：**

```
/home/ubuntu/codes/ai-writing/PROMPT-hottrend-series.md
```

### 流程概览

```
Step 1: 读取 plan.md → 提取 Part N 的角度/受众/素材/钩子
Step 2: 创建文章目录 + context.md（系列上下文）
Step 3: 执行 PROMPT-hottrend.md 完整 11 步流程（带系列调整）
Step 4: 系列收尾（导航 + 钩子 + 更新 plan.md）
```

### 系列调整（vs 普通 hottrend-article）

| 步骤 | 调整内容 |
|------|---------|
| Step 1（创建目录）| 跳过，使用 Step 2 的目录 |
| Step 2（抓取聚合）| 使用 context.md 中的素材方向作为关键词 |
| Step 3（撰写初稿）| 注入系列上下文，按 context.md 的角度/受众写作 |
| Step 6（精修二稿）| 注入系列上下文，确保差异化 |
| 最终收尾 | 追加系列导航 + 结尾钩子 |

### context.md 内容

从 plan.md 自动提取，包含：
- 系列信息（名称、篇数、标题前缀）
- 写作角度、目标受众、素材方向
- 结尾钩子（预告下一篇）
- 已完成篇目（避免内容重复）
- 系列导航（前后篇标题）

## Output

```
articles/YYYYMMDD-<series-name>-part<N>/
├── context.md              # 系列上下文（关键！）
├── images/
├── raw/
├── output/
│   ├── images -> ../images
│   ├── v1_draft.md
│   ├── v2_refined.md
│   └── v3_final.md         # 含系列导航 + 结尾钩子
└── process/
    └── pipeline.log
```

## Series Finishing

完成后自动：
1. 在 v3_final.md 末尾追加系列导航区块
2. 追加结尾钩子（预告下一篇）
3. 更新 plan.md: status → done, 填入 article_dir
