# DEV.to Search

Search tech articles on DEV.to via public API.

## API Endpoint

```
https://dev.to/api/articles
```

## Search Articles

```bash
curl -s "https://dev.to/api/articles?tag={keyword}&per_page=50" | \
  jq '.[] | {
    title: .title,
    url: .url,
    author: .user.username,
    tags: .tag_list,
    reactions: .positive_reactions_count,
    comments: .comments_count,
    date: .published_at,
    reading_time: .reading_time_minutes
  }'
```

## Search by Tag

```bash
curl -s "https://dev.to/api/articles?tag=ai,machinelearning&per_page=50&top=7"
```

## Popular Tags (AI/Tech)

| Tag | Description |
|-----|-------------|
| ai | Artificial Intelligence |
| machinelearning | Machine Learning |
| llm | Large Language Models |
| python | Python programming |
| javascript | JavaScript |
| webdev | Web development |
| devops | DevOps |
| tutorial | Tutorials |

## Sort Options

- Default: by `published_at` (recent)
- `top=7` - Top of past week
- `top=30` - Top of past month
- `top=365` - Top of past year

## Search Multiple Tags

```bash
curl -s "https://dev.to/api/articles?tag=ai&tag=langchain&per_page=30"
```

## Output Format

```markdown
## DEV.to Articles

| # | Title | Author | Reactions | Comments | Read Time |
|---|-------|--------|-----------|----------|-----------|
| 1 | [Title](url) | @author | 500 | 50 | 8 min |

### Popular Tags
- #ai (20 articles)
- #machinelearning (15 articles)
- #llm (10 articles)
```

## Rate Limits

- No authentication required for read
- 30 requests per 30 seconds
