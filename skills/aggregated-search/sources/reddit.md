# Reddit Search

Search Reddit content using alternative APIs due to Reddit's rate limiting and blocking of direct JSON API access.

## Problem: Reddit API Rate Limiting (2024-2025)

Reddit has significantly restricted access to their public JSON API:
- Direct requests to `reddit.com/search.json` often return HTML blocks
- Both `www.reddit.com` and `old.reddit.com` APIs are affected
- Rate limits are strictly enforced (10 req/min unauthenticated, 60 req/min with OAuth)
- User-Agent headers alone are no longer sufficient

## Recommended Solutions

### 1. Pullpush.io (Primary - Recommended)

Pullpush.io provides a reliable Reddit archive API that indexes Reddit content.

**Search Posts:**
```bash
curl -s "https://api.pullpush.io/reddit/search/submission/?q={keyword}&size=50&sort=desc&sort_type=created_utc" | \
  jq '.data[] | {
    title: .title,
    subreddit: .subreddit,
    url: ("https://reddit.com/r/" + .subreddit + "/comments/" + .id),
    score: .score,
    comments: .num_comments,
    author: .author,
    date: (.created_utc | todate)
  }'
```

**Search Comments:**
```bash
curl -s "https://api.pullpush.io/reddit/search/comment/?q={keyword}&size=50&sort=desc&sort_type=created_utc" | \
  jq '.data[] | {
    body: .body[:200],
    subreddit: .subreddit,
    author: .author,
    score: .score,
    date: (.created_utc | todate),
    url: ("https://reddit.com/r/" + .subreddit + "/comments/" + .link_id[3:] + "/_/" + .id)
  }'
```

**Filter by Subreddit:**
```bash
curl -s "https://api.pullpush.io/reddit/search/submission/?q={keyword}&subreddit=MachineLearning,artificial,LocalLLaMA&size=50"
```

**Pullpush.io Parameters:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `q` | Search query | `q=claude%20ai` |
| `size` | Number of results (max 100) | `size=50` |
| `sort` | Sort direction | `sort=desc` |
| `sort_type` | Sort field (created_utc, score) | `sort_type=score` |
| `subreddit` | Filter by subreddit(s) | `subreddit=LocalLLaMA` |
| `author` | Filter by author | `author=username` |
| `after` | Results after epoch time | `after=1704067200` |
| `before` | Results before epoch time | `before=1735689600` |

### 2. Exa API (Alternative for Semantic Search)

Exa provides AI-powered search that can find Reddit discussions. Useful when you need semantic/neural search.

```bash
curl -s -X POST "https://api.exa.ai/search" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_EXA_API_KEY" \
  -d '{
    "query": "{keyword} site:reddit.com",
    "type": "auto",
    "numResults": 20,
    "contents": {
      "text": true
    }
  }' | jq '.results[] | {title: .title, url: .url, text: .text[:300]}'
```

Note: Exa searches indexed content and may not have the latest posts.

### 3. Official Reddit API (With OAuth - Fallback)

If you need real-time data and have OAuth credentials:

```bash
# First get access token
ACCESS_TOKEN=$(curl -s -X POST "https://www.reddit.com/api/v1/access_token" \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -d "grant_type=client_credentials" \
  -A "aggregated-search/1.0" | jq -r '.access_token')

# Then search with token
curl -s "https://oauth.reddit.com/search.json?q={keyword}&sort=relevance&t=week&limit=50" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: aggregated-search/1.0" | \
  jq '.data.children[].data | {
    title: .title,
    subreddit: .subreddit,
    url: ("https://reddit.com" + .permalink),
    score: .score
  }'
```

## Recommended Subreddits

| Subreddit | Focus |
|-----------|-------|
| r/MachineLearning | ML research |
| r/artificial | AI general |
| r/LocalLLaMA | Local LLMs |
| r/singularity | AI future |
| r/programming | Programming |
| r/technology | Tech news |
| r/startups | Startup news |
| r/ClaudeAI | Claude discussions |

## Output Format

```markdown
## Reddit

| # | Title | Subreddit | Score | Comments | Date |
|---|-------|-----------|-------|----------|------|
| 1 | [Title](url) | r/MachineLearning | 500 | 100 | 2026-02-01 |

### Active Subreddits
- r/MachineLearning (15 posts)
- r/artificial (10 posts)
```

## Rate Limits & Best Practices

### Pullpush.io
- No authentication required
- Generous rate limits for reasonable use
- Slight delay in indexing (not real-time)

### Exa API
- Requires API key
- Semantic search capabilities
- Good for finding relevant discussions

### Official Reddit API
- OAuth required for reliable access
- 60 requests/minute with authentication
- Real-time data access

## Comparison

| Method | Auth Required | Real-time | Rate Limits | Best For |
|--------|--------------|-----------|-------------|----------|
| Pullpush.io | No | Near real-time | Generous | Most use cases |
| Exa API | API Key | Indexed | Per plan | Semantic search |
| Reddit OAuth | OAuth | Yes | 60 req/min | Real-time needs |

## Troubleshooting

**If Pullpush.io returns empty results:**
- Check if the query is URL-encoded
- Try broader search terms
- The content may not be indexed yet (wait a few hours)

**If Reddit blocks your request:**
- Use Pullpush.io instead
- Get OAuth credentials for official API
- Check if your IP is temporarily blocked
