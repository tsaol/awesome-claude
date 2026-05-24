---
name: hottrend-quick
description: Quick photo essay pipeline for hot topics. Produces ~600 word image-driven articles using Claude Opus + Kimi K2.5 refinement. 7-step fast workflow.
---

# Hottrend Quick - 热点图文速报

从热点话题或新闻链接出发，通过 7 步精简 pipeline 快速产出 ~600 字 Photo Essay 风格图文速报。

## Usage

```
/hottrend-quick <topic_or_urls> [options]
```

**Examples:**
```
/hottrend-quick "GPT-5 发布"
/hottrend-quick https://url1.com https://url2.com
/hottrend-quick "Apple WWDC 2026" --no-publish
```

## Pipeline (7 Steps)

**执行此 skill 时，必须读取并严格按照以下 PROMPT 文件执行：**

```
/home/ubuntu/codes/ai-writing/PROMPT-hottrend-quick.md
```

### 流程概览

```
Step 1: 创建项目目录 (articles/YYYYMMDD-HHMMSS-hottrend-quick/)
Step 2: hottrend-aggregator        → raw/aggregated.md + images/
Step 3: hottrend-quick-draft(Opus) → output/v1_quick.md
Step 4: hottrend-quick-refiner(Kimi K2.5) → output/v2_kimi.md
Step 5: title-generator(Opus)      → 5 个备选标题
Step 6: de-ai-filter(Opus)         → output/v3_final.md
Step 7: wechat-mcp                 → 公众号草稿箱
```

### Model Strategy

| Step | Model | Reason |
|------|-------|--------|
| quick-draft | Claude Opus | 初稿生成质量高 |
| quick-refiner | Kimi K2.5 | 口语化润色最自然 |
| title/de-ai | Claude Opus | 质量把关 |

### Agents (in ~/codes/ai-writing/.claude/agents/)

| Step | Agent | Role |
|------|-------|------|
| 2 | hottrend-aggregator | 多源抓取聚合（降低 Quality Gate） |
| 3 | hottrend-quick-draft | Photo Essay 风格初稿，图片驱动叙事 |
| 4 | hottrend-quick-refiner | Kimi K2.5 润色（via invoke_model.py） |

## vs Full Article

| 对比 | /hottrend-article | /hottrend-quick |
|------|-------------------|-----------------|
| 步骤 | 11 步 | 7 步 |
| 字数 | 2000-3000 字 | 500-700 字 |
| 图片 | 3-6 张 | 5-8 张 |
| 风格 | 深度综述 | Photo Essay 图文速报 |
| 模型 | 全 Claude Opus | Opus + Kimi K2.5 |
| 砍掉 | — | reader-critic, analyzer, refiner, diagram-gen, image-gen, wx-packager |

## Output Structure

```
articles/YYYYMMDD-HHMMSS-hottrend-quick/
├── images/                 # 抓取的图片
├── raw/
│   ├── aggregated.md       # 聚合素材
│   └── source_*.md         # 各来源原文
├── output/
│   ├── images -> ../images # 符号链接
│   ├── v1_quick.md         # 图文速报初稿 (Opus)
│   ├── v2_kimi.md          # Kimi K2.5 润色稿
│   └── v3_final.md         # 最终稿
└── process/
    ├── pipeline.log        # 执行日志
    └── step4_input.md      # Kimi 调用输入
```

## Key Rules

- 所有步骤的详细规则在 PROMPT-hottrend-quick.md 中定义
- 图片是主要叙事工具，文字围绕图片展开
- 图片说明 ≤20 字（"这是什么"），点评 50-100 字（"所以呢"）
- 全文 500-700 字，5-8 张图片
- output/ 必须创建 images 符号链接
