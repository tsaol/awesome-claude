# Hacker News Search

Search Hacker News via Algolia API (free, no auth required).

## API Endpoint

```
https://hn.algolia.com/api/v1/search
```

## Search Stories

```bash
curl -s "https://hn.algolia.com/api/v1/search?query={keyword}&tags=story&hitsPerPage=50" | \
  jq '.hits[] | {
    title: .title,
    url: .url,
    points: .points,
    comments: .num_comments,
    author: .author,
    date: .created_at,
    hn_url: ("https://news.ycombinator.com/item?id=" + (.objectID | tostring))
  }'
```

## Search by Date (Recent)

```bash
curl -s "https://hn.algolia.com/api/v1/search_by_date?query={keyword}&tags=story&hitsPerPage=50" | \
  jq '.hits[] | {
    title: .title,
    url: .url,
    points: .points,
    comments: .num_comments,
    date: .created_at
  }'
```

## Filter by Time Range

Last 7 days:
```bash
WEEK_AGO=$(date -d '7 days ago' +%s)
curl -s "https://hn.algolia.com/api/v1/search?query={keyword}&tags=story&numericFilters=created_at_i>${WEEK_AGO}&hitsPerPage=50"
```

## Tags

- `story` - Main stories
- `comment` - Comments
- `ask_hn` - Ask HN posts
- `show_hn` - Show HN posts
- `front_page` - Front page items

## Output Format

```markdown
## Hacker News

| # | Title | Points | Comments | Date |
|---|-------|--------|----------|------|
| 1 | [Title](hn_url) | 500 | 200 | 2026-02-01 |
| 2 | [Title](hn_url) | 300 | 150 | 2026-02-01 |

### Top Discussions
1. [Title](url) - 500 points, 200 comments
   > Top comment preview...
```

## Rate Limits

- No authentication required
- 10,000 requests/hour
