# ArXiv Search

Search academic papers on ArXiv via public API.

## Important: API Reliability Issues

The ArXiv API can be unreliable with empty responses or timeouts. Key fixes:

1. **Use HTTPS** (not HTTP) - more reliable
2. **Rate limit**: Wait 3+ seconds between requests
3. **Use arxiv Python library** - handles retries automatically
4. **Have fallbacks ready** - Semantic Scholar, Papers With Code

## API Endpoint

```
https://export.arxiv.org/api/query
```

**Note:** Use HTTPS instead of HTTP for better reliability.

## Method 1: Direct API (with HTTPS)

```bash
curl -s --max-time 30 "https://export.arxiv.org/api/query?search_query=all:{keyword}&start=0&max_results=50&sortBy=submittedDate&sortOrder=descending"
```

### URL Encoding Tips

- Replace spaces with `+` or `%20`
- For exact phrases, use URL-encoded quotes: `%22machine%20learning%22`
- Boolean operators: `AND`, `OR`, `ANDNOT` (uppercase)

## Method 2: arxiv Python Library (Recommended)

The `arxiv` Python library is more reliable with built-in retry logic.

### Installation

```bash
pip install arxiv
```

### Usage

```python
import arxiv

# Create client with retry configuration
client = arxiv.Client(
    page_size=50,
    delay_seconds=3.0,  # Respect rate limits
    num_retries=3
)

# Search papers
search = arxiv.Search(
    query='{keyword}',  # or 'cat:cs.AI AND {keyword}'
    max_results=50,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
)

for result in client.results(search):
    print(f"Title: {result.title}")
    print(f"URL: {result.entry_id}")
    print(f"Abstract: {result.summary[:200]}...")
    print(f"Authors: {', '.join([a.name for a in result.authors])}")
    print(f"Categories: {', '.join(result.categories)}")
    print(f"Published: {result.published.date()}")
```

## Method 3: Using WebFetch

```
WebFetch: https://export.arxiv.org/api/query?search_query=all:{keyword}&max_results=50&sortBy=submittedDate
Prompt: Extract paper titles, URLs, authors, abstracts, and dates. Format as markdown table.
```

## Fallback: Semantic Scholar API

If ArXiv is slow/empty, use Semantic Scholar:

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={keyword}&limit=50&fields=title,url,abstract,year,authors,externalIds"
```

This returns papers including those from ArXiv (check `externalIds.ArXiv`).

## Fallback: Papers With Code API

```bash
curl -s "https://paperswithcode.com/api/v1/papers/?q={keyword}&page=1"
```

Returns papers with associated code repositories.

## Search Fields

- `all:` - All fields
- `ti:` - Title
- `au:` - Author
- `abs:` - Abstract
- `cat:` - Category

## Categories (AI/ML related)

| Category | Description |
|----------|-------------|
| cs.AI | Artificial Intelligence |
| cs.CL | Computation and Language (NLP) |
| cs.CV | Computer Vision |
| cs.LG | Machine Learning |
| cs.NE | Neural and Evolutionary Computing |
| stat.ML | Statistics - Machine Learning |

## Combined Search Examples

```
# Category + keyword
search_query=cat:cs.AI+AND+ti:LLM

# Multiple keywords
search_query=all:machine+AND+all:learning

# Exact phrase (URL encoded)
search_query=all:%22large%20language%20model%22

# Author + category
search_query=au:hinton+AND+cat:cs.LG
```

## Output Format

```markdown
## ArXiv Papers

| # | Title | Authors | Category | Date |
|---|-------|---------|----------|------|
| 1 | [Title](arxiv_url) | Author1, Author2 | cs.AI | 2026-02-01 |

### Abstract Summaries

**[Paper Title](url)**
> First 200 chars of abstract...

**[Paper Title](url)**
> First 200 chars of abstract...
```

## Rate Limits & Best Practices

- **No authentication required**
- **1 request per 3 seconds minimum** - critical for reliability
- **Use HTTPS** - HTTP endpoint is less reliable
- **max_results limit**: 2000 per request, 30000 total per query
- **Implement retries** with exponential backoff
- For bulk downloads: use arXiv S3 bucket or OAI-PMH interface

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Empty responses | Use HTTPS, add delay, retry 3x |
| Timeouts | Reduce max_results, use arxiv library |
| Inconsistent results | This is a known ArXiv API issue; use retries |
| Rate limited | Wait 3+ seconds between requests |
