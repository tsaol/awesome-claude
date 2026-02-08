# Tavily Search API

AI-optimized search API that aggregates web results.

## API Endpoint

```
https://api.tavily.com/search
```

## Environment

```bash
export TAVILY_API_KEY="your-api-key"
```

## Search Request

```bash
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "'$TAVILY_API_KEY'",
    "query": "{keyword}",
    "search_depth": "advanced",
    "include_answer": true,
    "include_raw_content": false,
    "max_results": 20,
    "include_domains": [],
    "exclude_domains": []
  }' | jq '.results[] | {
    title: .title,
    url: .url,
    content: .content,
    score: .score
  }'
```

## Search Depth Options

- `basic` - Fast, fewer results
- `advanced` - Comprehensive, more results

## Filter by Domains

Include only tech sites:
```json
{
  "include_domains": [
    "techcrunch.com",
    "theverge.com",
    "wired.com",
    "arstechnica.com",
    "venturebeat.com"
  ]
}
```

## Output Format

```markdown
## Tavily Web Search

| # | Title | Source | Relevance |
|---|-------|--------|-----------|
| 1 | [Title](url) | techcrunch.com | 0.95 |
| 2 | [Title](url) | theverge.com | 0.90 |

### AI Summary
> {tavily_answer}
```

## Pricing

- Free: 1000 searches/month
- Pay-as-you-go: $0.01/search
- Best for: Comprehensive web coverage
