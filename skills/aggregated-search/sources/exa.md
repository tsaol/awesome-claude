# Exa Search API

AI-native search API (formerly Metaphor). Optimized for finding links that LLMs can use.

## API Endpoint

```
https://api.exa.ai/search
```

## Environment

```bash
export EXA_API_KEY="your-api-key"
```

## Search Request

```bash
curl -s -X POST "https://api.exa.ai/search" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $EXA_API_KEY" \
  -d '{
    "query": "{keyword}",
    "numResults": 20,
    "type": "neural",
    "useAutoprompt": true,
    "startPublishedDate": "2024-01-01"
  }' | jq '.results[] | {
    title: .title,
    url: .url,
    publishedDate: .publishedDate,
    score: .score
  }'
```

## Search Types

| Type | Description |
|------|-------------|
| `neural` | Semantic search (recommended) |
| `keyword` | Traditional keyword search |
| `auto` | Auto-select based on query |

## Get Contents

After search, get full content:
```bash
curl -s -X POST "https://api.exa.ai/contents" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $EXA_API_KEY" \
  -d '{
    "ids": ["id1", "id2"],
    "text": true,
    "highlights": true
  }'
```

## Find Similar

Find pages similar to a URL:
```bash
curl -s -X POST "https://api.exa.ai/findSimilar" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $EXA_API_KEY" \
  -d '{
    "url": "https://example.com/article",
    "numResults": 10
  }'
```

## Search Options

| Option | Description |
|--------|-------------|
| `numResults` | Number of results (max 100) |
| `useAutoprompt` | Auto-optimize query (recommended) |
| `startPublishedDate` | Filter by date (ISO 8601) |
| `endPublishedDate` | Filter by date |
| `includeDomains` | Only these domains |
| `excludeDomains` | Exclude these domains |

## Filter by Domain

Tech sites only:
```json
{
  "includeDomains": [
    "techcrunch.com",
    "theverge.com",
    "arstechnica.com",
    "venturebeat.com",
    "wired.com"
  ]
}
```

## Output Format

```markdown
## Exa Search

| # | Title | Source | Date | Score |
|---|-------|--------|------|-------|
| 1 | [Title](url) | techcrunch.com | 2026-02-08 | 0.95 |
| 2 | [Title](url) | theverge.com | 2026-02-07 | 0.90 |

### Highlights
- Key point from article 1
- Key point from article 2
```

## Pricing

- Free: 1000 searches/month
- Pay-as-you-go: $0.001/search
- Better for: High-quality curated results

## vs Tavily

| Feature | Exa | Tavily |
|---------|-----|--------|
| Search Type | Neural/Semantic | Web crawl |
| Find Similar | ✅ | ❌ |
| Auto-prompt | ✅ | ❌ |
| Content Extract | ✅ | ✅ |
| Price | $0.001/search | $0.01/search |
