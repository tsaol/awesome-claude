# Tech News Sites

Aggregate tech news via WebFetch.

## Sites List

| Site | URL | Focus |
|------|-----|-------|
| TechCrunch | techcrunch.com | Startups, Tech |
| The Verge | theverge.com | Consumer Tech |
| Wired | wired.com | Tech Culture |
| Ars Technica | arstechnica.com | Deep Tech |
| VentureBeat | venturebeat.com | AI/Enterprise |
| MIT Tech Review | technologyreview.com | Tech Analysis |
| IEEE Spectrum | spectrum.ieee.org | Engineering |
| The Information | theinformation.com | Tech Business |

## Search via WebFetch

### TechCrunch
```
WebFetch: https://techcrunch.com/tag/{keyword}/
Prompt: Extract article titles, URLs, dates, and summaries. Return as markdown table.
```

### VentureBeat AI
```
WebFetch: https://venturebeat.com/?s={keyword}
Prompt: Extract article titles, URLs, dates, and summaries from search results.
```

### Ars Technica
```
WebFetch: https://arstechnica.com/search/?q={keyword}
Prompt: Extract article titles, URLs, dates, and summaries.
```

## RSS Feeds (Alternative)

| Site | RSS URL |
|------|---------|
| TechCrunch | techcrunch.com/feed/ |
| The Verge | theverge.com/rss/index.xml |
| Ars Technica | feeds.arstechnica.com/arstechnica/index |
| Wired | wired.com/feed/rss |

## Output Format

```markdown
## Tech News

### TechCrunch
| # | Title | Date |
|---|-------|------|
| 1 | [Title](url) | 2026-02-08 |

### VentureBeat
| # | Title | Date |
|---|-------|------|
| 1 | [Title](url) | 2026-02-08 |

### The Verge
| # | Title | Date |
|---|-------|------|
| 1 | [Title](url) | 2026-02-08 |
```

## Notes

- Some sites may block automated access
- Use Tavily as backup for blocked sites
- Respect robots.txt
