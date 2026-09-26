---
name: aggregated-search
description: Multi-source content aggregation for hot-topic / trend research. Searches GitHub, Hacker News, Reddit, DEV.to, ArXiv, Semantic Scholar, Tavily, Exa, tech news, AI lab and cloud blogs, Chinese tech media (36氪/知乎/掘金/机器之心) and more in parallel, then dedupes into raw/aggregated.md. Use when the user asks to research, survey or collect recent content/discussions on a topic across many sources, or invokes /aggregated-search.
---

# Aggregated Search Skill

Multi-source content aggregation for hot topics research. Supports 20+ data sources.

## Usage

```
/aggregated-search <keyword> [options]
```

**Options:**
- `--sources=all` - Search all sources (default)
- `--sources=github,hn,reddit` - Specific sources (use the **Name** column below, or a group)
- `--limit=50` - Max results per source (default: 50)
- `--days=7` - Content age limit in days (default: 7)
- `--lang=en` - Language: en, zh, all (default: all)
- `--expand` - Enable query expansion (auto-generate related terms)

**Examples:**
```
/aggregated-search "agentic AI"
/aggregated-search "LLM agents" --sources=github,hn,arxiv
/aggregated-search "大模型" --sources=chinese --lang=zh
/aggregated-search "RAG" --limit=100 --days=30
```

## Supported Sources (20+)

The **Name** column is the value accepted by `--sources=`; the **File** column is the instruction file under `sources/` to read for that name. Several names can share one file (e.g. `36kr` and `zhihu` both live in `chinese-tech.md`) — in that case read the file once and only run the section for the requested site.

### Code & Projects
| Name | Source | File | API | Free |
|------|--------|------|-----|------|
| `github` | GitHub | github.md | gh api | ✅ |
| `papers-with-code` | Papers With Code ⚠️ **Discontinued** | papers-with-code.md | — | — |

> ⚠️ Papers With Code was shut down in July 2025 and now redirects to Hugging Face Papers; its API no longer works. Skip it by default and use Hugging Face Papers instead (`WebFetch: https://huggingface.co/papers?q={keyword}` or the trending list at `https://huggingface.co/papers`), plus `github` for implementation code.

### Tech Communities
| Name | Source | File | API | Free |
|------|--------|------|-----|------|
| `hn` / `hackernews` | Hacker News | hackernews.md | Algolia | ✅ |
| `reddit` | Reddit | reddit.md | JSON | ✅ |
| `devto` | DEV.to | devto.md | REST | ✅ |
| `producthunt` | Product Hunt | producthunt.md | GraphQL | ✅ |

### Academic
| Name | Source | File | API | Free |
|------|--------|------|-----|------|
| `arxiv` | ArXiv (see also arxiv-categories.md) | arxiv.md | XML | ✅ |
| `semantic-scholar` | Semantic Scholar | semantic-scholar.md | REST | ✅ |
| `papers-with-code` | Papers With Code ⚠️ **Discontinued** (use Hugging Face Papers) | papers-with-code.md | — | — |

### News, Media & Blogs
| Name | Source | File | API | Free |
|------|--------|------|-----|------|
| `tech-news` | Tech News (Multi) | tech-news.md | WebFetch | ✅ |
| `medium` | Medium | medium.md | WebFetch | ✅ |
| `ai-labs` | AI Labs official blogs (OpenAI/Anthropic/Google/DeepMind/Meta/...) | ai-labs.md | WebFetch | ✅ |
| `cloud-ai` | Cloud AI blogs (AWS/GCP/Azure) | cloud-ai.md | WebFetch | ✅ |
| `tech-bloggers` | Tech bloggers & newsletters (Simon Willison, Latent Space, ...) | tech-bloggers.md | WebFetch | ✅ |
| `agent-frameworks` | Agent framework blogs (LangChain/LlamaIndex/CrewAI/...) | agent-frameworks.md | WebFetch | ✅ |

### Chinese Sources (中文源)
| Name | Source | File | API | Free |
|------|--------|------|-----|------|
| `36kr`, `sspai`, `juejin`, `zhihu`, `jiqizhixin` | 36氪/少数派/掘金/知乎/机器之心 | chinese-tech.md | Mixed | ✅ |
| `chinese-media` | 中文 AI 媒体 (机器之心/量子位/钛媒体/InfoQ/雷锋网...) | chinese-media.md | WebFetch | ✅ |

### Social Media
| Name | Source | File | API | Free |
|------|--------|------|-----|------|
| `twitter` | Twitter/X | twitter.md | API (paid) / Nitter ⚠️ | ⚠️ |
| `youtube` | YouTube | youtube.md | WebFetch | ✅ |

> ⚠️ Public Nitter instances are unreliable (most were shut down or rate-limited after X's 2024 API changes). Treat Nitter results as best-effort; prefer the official API if `TWITTER_BEARER_TOKEN` is set, or fall back to `tavily`/`exa` with `site:x.com {keyword}`.

### Meta Search (Recommended)
| Name | Source | File | API | Free |
|------|--------|------|-----|------|
| `tavily` | **Tavily** | tavily.md | REST | 1000/mo |
| `exa` | **Exa** (AI-native search) | exa.md | REST | 1000/mo |

## Source Groups

Use these shortcuts for common combinations:

| Group | Sources |
|-------|---------|
| `--sources=code` | github (papers-with-code discontinued → Hugging Face Papers) |
| `--sources=community` | hn, reddit, devto |
| `--sources=academic` | arxiv, semantic-scholar (papers-with-code discontinued → Hugging Face Papers) |
| `--sources=news` | tavily, exa, tech-news, medium |
| `--sources=blogs` | ai-labs, cloud-ai, tech-bloggers, agent-frameworks |
| `--sources=chinese` | 36kr, sspai, juejin, zhihu, jiqizhixin, chinese-media |
| `--sources=social` | twitter, youtube, producthunt |
| `--sources=all` | All sources |

## Workflow

### Step 0: Query Expansion (if --expand)
If `--expand` is enabled, generate related terms before searching:

```
Original: "agentic commerce"
    ↓
Expanded (max 5):
  - agentic commerce (original)
  - AI shopping agent
  - conversational commerce
  - e-commerce AI assistant
  - 智能购物
```

Use the prompt in `sources/query-expansion.md` to generate max 4 related terms (5 total).

### Step 1: Parse Input
Extract keyword, sources, limit, days, language from user input.

### Step 2: Parallel Search
**CRITICAL:** Search all sources in parallel using multiple tool calls in a single message.

For each source:
1. Look up the source name in the **Name** column of the tables above and read the matching file from `sources/` (e.g. `hn` → `sources/hackernews.md`, `zhihu` → `sources/chinese-tech.md`). Do not construct `sources/{name}.md` blindly — short names like `hn`/`36kr`/`zhihu` have no file of their own. If a name is unknown, report it and skip it
2. Execute API call or WebFetch
3. Parse results

### Step 3: Aggregate & Deduplicate
1. Merge all results
2. Deduplicate by URL and title similarity (>80% = duplicate)
3. Sort by: relevance score, date, engagement
4. Tag with source name

### Step 4: Output
Generate `raw/aggregated.md`:

```markdown
# Aggregated Search: {keyword}

**Sources:** {count} sources searched
**Results:** {total} unique items
**Generated:** {timestamp}

---

## Summary (via Tavily AI)
> AI-generated summary of the topic...

## GitHub ({count})
| # | Repository | Stars | Description |
|---|------------|-------|-------------|

## Hacker News ({count})
| # | Title | Points | Comments |
|---|-------|--------|----------|

## Academic Papers ({count})
| # | Title | Year | Citations |
|---|-------|------|-----------|

## News & Blogs ({count})
| # | Title | Source | Date |
|---|-------|--------|------|

## Chinese Sources ({count})
| # | 标题 | 来源 | 日期 |
|---|------|------|------|

---

## Statistics
- Total sources: {sources_count}
- Total results: {total_count}
- Unique results: {unique_count}
- Date range: {earliest} to {latest}
```

## Environment Variables

```bash
# Required for full functionality
export TAVILY_API_KEY="your-key"        # Tavily search
export EXA_API_KEY="your-key"           # Exa search (optional)

# Optional
export YOUTUBE_API_KEY="your-key"       # YouTube API
export TWITTER_BEARER_TOKEN="your-key"  # Twitter API (paid)
export PRODUCTHUNT_TOKEN="your-key"     # Product Hunt API
```

## Integration

Works with ai-writing hottrend pipeline:

```
/aggregated-search "topic"
        ↓
  raw/aggregated.md
        ↓
  hottrend-draft agent
        ↓
  output/v1_draft.md
```
