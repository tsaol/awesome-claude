# Aggregated Search Skill

Multi-source content aggregation for hot topics research. Supports 15+ data sources.

## Usage

```
/aggregated-search <keyword> [options]
```

**Options:**
- `--sources=all` - Search all sources (default)
- `--sources=github,hn,reddit` - Specific sources
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

## Supported Sources (15+)

### Code & Projects
| Source | File | API | Free |
|--------|------|-----|------|
| GitHub | github.md | gh api | ✅ |
| Papers With Code | papers-with-code.md | REST | ✅ |

### Tech Communities
| Source | File | API | Free |
|--------|------|-----|------|
| Hacker News | hackernews.md | Algolia | ✅ |
| Reddit | reddit.md | JSON | ✅ |
| DEV.to | devto.md | REST | ✅ |
| Product Hunt | producthunt.md | GraphQL | ✅ |

### Academic
| Source | File | API | Free |
|--------|------|-----|------|
| ArXiv | arxiv.md | XML | ✅ |
| Semantic Scholar | semantic-scholar.md | REST | ✅ |
| Papers With Code | papers-with-code.md | REST | ✅ |

### News & Media
| Source | File | API | Free |
|--------|------|-----|------|
| Tech News (Multi) | tech-news.md | WebFetch | ✅ |
| Medium | medium.md | WebFetch | ✅ |

### Chinese Sources (中文源)
| Source | File | API | Free |
|--------|------|-----|------|
| 36氪/少数派/掘金/知乎/机器之心 | chinese-tech.md | Mixed | ✅ |

### Social Media
| Source | File | API | Free |
|--------|------|-----|------|
| Twitter/X | twitter.md | Nitter | ✅ |
| YouTube | youtube.md | WebFetch | ✅ |

### Meta Search (Recommended)
| Source | File | API | Free |
|--------|------|-----|------|
| **Tavily** | tavily.md | REST | 1000/mo |

## Source Groups

Use these shortcuts for common combinations:

| Group | Sources |
|-------|---------|
| `--sources=code` | github, papers-with-code |
| `--sources=community` | hn, reddit, devto |
| `--sources=academic` | arxiv, semantic-scholar, papers-with-code |
| `--sources=news` | tavily, tech-news, medium |
| `--sources=chinese` | 36kr, sspai, juejin, zhihu, jiqizhixin |
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
1. Read source instruction from `sources/{source}.md`
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
