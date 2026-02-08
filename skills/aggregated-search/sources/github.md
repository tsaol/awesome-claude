# GitHub Search

Search GitHub repositories and code using `gh api`.

## Repository Search

```bash
gh api search/repositories \
  -X GET \
  -f q="{keyword} in:name,description,readme" \
  -f sort=stars \
  -f order=desc \
  -f per_page=50 \
  --jq '.items[] | {
    name: .full_name,
    url: .html_url,
    stars: .stargazers_count,
    description: .description,
    language: .language,
    updated: .updated_at,
    topics: .topics
  }'
```

## Code Search

```bash
gh api search/code \
  -X GET \
  -f q="{keyword}" \
  -f per_page=30 \
  --jq '.items[] | {
    repo: .repository.full_name,
    path: .path,
    url: .html_url
  }'
```

## Multiple Query Strategy

For comprehensive results, search with variations:

1. Main keyword: `{keyword}`
2. With "awesome": `awesome {keyword}`
3. With "agent": `{keyword} agent`
4. With "framework": `{keyword} framework`

## Output Format

```markdown
## GitHub Repositories

| # | Repository | Stars | Language | Description |
|---|------------|-------|----------|-------------|
| 1 | [owner/repo](url) | 1.2k | Python | ... |
| 2 | [owner/repo](url) | 800 | TypeScript | ... |

### Trending Topics
- topic1 (15 repos)
- topic2 (12 repos)
```

## Rate Limits

- Authenticated: 5000 requests/hour
- Search: 30 requests/minute
- Use `--paginate` for large result sets
