# Medium Search

Search tech articles on Medium.

## Search via WebFetch

```
WebFetch: https://medium.com/search?q={keyword}
Prompt: Extract article titles, authors, publication names, claps count, and URLs. Return as markdown table.
```

## Tag-based Search

```
WebFetch: https://medium.com/tag/{keyword}/latest
Prompt: Extract latest articles with title, author, publication, and URL.
```

## Popular Publications

| Publication | Focus | URL |
|-------------|-------|-----|
| Towards Data Science | Data/ML | towardsdatascience.com |
| Better Programming | Dev | betterprogramming.pub |
| The Startup | Startups | medium.com/swlh |
| HackerNoon | Tech | hackernoon.com |
| freeCodeCamp | Learning | freecodecamp.org |
| Level Up Coding | Dev | levelup.gitconnected.com |

## Search Specific Publication

```
WebFetch: https://towardsdatascience.com/search?q={keyword}
Prompt: Extract articles about {keyword} with title, author, claps, and URL.
```

## Output Format

```markdown
## Medium Articles

| # | Title | Author | Publication | Claps |
|---|-------|--------|-------------|-------|
| 1 | [Title](url) | @author | Towards Data Science | 5.2k |
| 2 | [Title](url) | @author | Better Programming | 2.1k |

### Top Writers
- @author1 (50 articles on topic)
- @author2 (30 articles on topic)
```

## Notes

- Medium has paywall for some articles
- Use archive.is for paywalled content
- Better to search specific publications
