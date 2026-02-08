# YouTube Search

Search YouTube for video content.

## YouTube Data API

```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q={keyword}&type=video&maxResults=50&key=$YOUTUBE_API_KEY" | \
  jq '.items[] | {
    title: .snippet.title,
    channel: .snippet.channelTitle,
    description: .snippet.description,
    url: ("https://youtube.com/watch?v=" + .id.videoId),
    date: .snippet.publishedAt
  }'
```

## Search via WebFetch

```
WebFetch: https://www.youtube.com/results?search_query={keyword}
Prompt: Extract video titles, channel names, view counts, and URLs. Return as markdown table.
```

## Filter Options

| Parameter | Values | Description |
|-----------|--------|-------------|
| order | date, rating, viewCount, relevance | Sort order |
| videoDuration | short, medium, long | Video length |
| publishedAfter | ISO 8601 date | After date |
| type | video, channel, playlist | Result type |

## AI/Tech Channels

| Channel | Focus |
|---------|-------|
| Two Minute Papers | AI research |
| Yannic Kilcher | ML papers |
| AI Explained | AI news |
| Fireship | Dev tutorials |
| NetworkChuck | Tech tutorials |
| Lex Fridman | AI interviews |

## Output Format

```markdown
## YouTube Videos

| # | Title | Channel | Views | Date |
|---|-------|---------|-------|------|
| 1 | [Title](url) | Two Minute Papers | 500k | 2026-02-08 |
| 2 | [Title](url) | Yannic Kilcher | 100k | 2026-02-07 |

### Top Channels for Topic
1. Two Minute Papers (10 videos)
2. Yannic Kilcher (8 videos)
```

## Notes

- API quota: 10,000 units/day free
- Search costs 100 units
- WebFetch works for basic search
