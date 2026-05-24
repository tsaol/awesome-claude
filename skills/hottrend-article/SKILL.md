---
name: hottrend-article
description: Full hottrend article pipeline. Aggregates sources, drafts, reviews, refines, generates images, and packages for WeChat publication. 11-step multi-agent workflow.
---

# Hottrend Article - 热点深度文章生产

从热点话题或新闻链接出发，通过 11 步 multi-agent pipeline 生产高质量公众号深度文章（2000-3000 字）。

## Usage

```
/hottrend-article <topic_or_urls> [options]
```

**Examples:**
```
/hottrend-article "OpenAI GPT-5 发布"
/hottrend-article https://url1.com https://url2.com https://url3.com
/hottrend-article "AI Agent 2026" --no-publish
```

## Pipeline (11 Steps)

**执行此 skill 时，必须读取并严格按照以下 PROMPT 文件执行：**

```
/home/ubuntu/codes/ai-writing/PROMPT-hottrend.md
```

### 流程概览

```
Step 1:  创建项目目录 (articles/YYYYMMDD-HHMMSS-hottrend/)
Step 2:  hottrend-aggregator    → raw/aggregated.md + images/
Step 3:  hottrend-draft         → output/v1_draft.md
Step 4:  hottrend-reader-critic → process/reader-critique.md
Step 5:  hottrend-analyzer      → process/analysis.md
Step 6:  hottrend-refiner       → output/v2_refined.md
Step 7:  hottrend-image-gen     → output/images/ + cover
Step 8:  blog-diagram-generator → Mermaid diagrams (按需)
Step 9:  title-generator        → 5 个备选标题
Step 10: de-ai-filter           → output/v3_final.md
Step 11: hottrend-wx-packager   → package.json + 发布
```

### Agents (in ~/codes/ai-writing/.claude/agents/)

| Step | Agent | Role |
|------|-------|------|
| 2 | hottrend-aggregator | 多源抓取聚合，Quality Gate 检查 |
| 3 | hottrend-draft | 撰写 ≥2000 字初稿，含数据表格 |
| 4 | hottrend-reader-critic | 行业读者视角审稿 |
| 5 | hottrend-analyzer | 运营+商业视角分析 |
| 6 | hottrend-refiner | 融合反馈精修二稿 |
| 7 | hottrend-image-gen | 选图/生图/配图 |
| 11 | hottrend-wx-packager | 微信公众号发布打包 |

## Output Structure

```
articles/YYYYMMDD-HHMMSS-hottrend/
├── images/                 # 统一图片目录
├── raw/
│   ├── aggregated.md       # 聚合素材
│   └── source_*.md         # 各来源原文
├── output/
│   ├── images -> ../images # 符号链接
│   ├── v1_draft.md         # 初稿
│   ├── v2_refined.md       # 精修稿
│   ├── v3_final.md         # 最终稿
│   └── package.json        # 发布素材包
└── process/
    ├── pipeline.log        # 执行日志
    ├── reader-critique.md  # 读者反馈
    └── analysis.md         # 运营分析
```

## Key Rules

- 所有步骤的详细规则在 PROMPT-hottrend.md 中定义
- 每完成一步必须写 pipeline.log
- output/ 必须创建 images 符号链接: `ln -s ../images output/images`
- 初稿 ≥2000 字，建议 2500-3000 字
- 必须包含 ≥3 张图片和 1-2 个数据表格
- 最终稿经 de-ai-filter 去除 AI 痕迹
