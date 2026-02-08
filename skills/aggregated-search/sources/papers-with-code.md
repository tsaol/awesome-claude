# Papers With Code API

ML papers with implementation code.

## API Endpoint

```
https://paperswithcode.com/api/v1/papers/
```

## Search Papers

```bash
curl -s "https://paperswithcode.com/api/v1/search/?q={keyword}" | \
  jq '.results[] | {
    title: .paper.title,
    url: .paper.url_abs,
    abstract: .paper.abstract[:200],
    published: .paper.published,
    github: .repository.url
  }'
```

## Get Trending Papers

```bash
curl -s "https://paperswithcode.com/api/v1/papers/?ordering=-github_stars" | \
  jq '.results[] | {
    title: .title,
    stars: .github_stars,
    url: .url_abs
  }'
```

## Search by Task

```bash
curl -s "https://paperswithcode.com/api/v1/tasks/?q={keyword}" | \
  jq '.results[] | {
    name: .name,
    description: .description,
    papers_count: .papers_count
  }'
```

## Output Format

```markdown
## Papers With Code

| # | Paper | GitHub | Stars |
|---|-------|--------|-------|
| 1 | [Title](paper_url) | [repo](github_url) | 5.2k |
| 2 | [Title](paper_url) | [repo](github_url) | 3.1k |

### Top Implementations
1. **[Paper](url)** - [GitHub](repo) - 5000 stars
   - Task: Language Modeling
   - Framework: PyTorch
```

## Rate Limits

- No authentication required
- Reasonable rate limiting
