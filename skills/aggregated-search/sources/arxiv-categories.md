# ArXiv Categories

Search specific ArXiv categories for academic papers.

## AI/ML Categories

| Category | Code | Description |
|----------|------|-------------|
| Artificial Intelligence | cs.AI | General AI |
| Computation and Language | cs.CL | NLP, LLMs |
| Computer Vision | cs.CV | Vision models |
| Machine Learning | cs.LG | ML algorithms |
| Information Retrieval | cs.IR | Search, RAG |
| Neural/Evolutionary | cs.NE | Neural networks |
| Robotics | cs.RO | Robotics, embodied AI |
| Machine Learning (Stats) | stat.ML | Statistical ML |

## Search by Category

### cs.AI (Artificial Intelligence)
```bash
curl -s "http://export.arxiv.org/api/query?search_query=cat:cs.AI+AND+all:{keyword}&start=0&max_results=20&sortBy=submittedDate&sortOrder=descending"
```

### cs.CL (NLP/LLMs)
```bash
curl -s "http://export.arxiv.org/api/query?search_query=cat:cs.CL+AND+all:{keyword}&start=0&max_results=20&sortBy=submittedDate&sortOrder=descending"
```

### Combined Categories
```bash
curl -s "http://export.arxiv.org/api/query?search_query=(cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG)+AND+all:{keyword}&max_results=30&sortBy=submittedDate"
```

## Via WebFetch

```
WebFetch: https://arxiv.org/search/?query={keyword}&searchtype=all&source=header&start=0
Prompt: Extract paper titles, authors, arxiv IDs, abstracts (first 100 chars), and submission dates. Return as markdown table.
```

## Recent Papers in Category

```
WebFetch: https://arxiv.org/list/cs.AI/recent
Prompt: Extract the 20 most recent papers with title, authors, arxiv ID.
```

## Output Format

```markdown
## ArXiv Papers

### cs.AI - Artificial Intelligence
| # | Title | Authors | Date |
|---|-------|---------|------|
| 1 | [Title](arxiv_url) | Author1, Author2 | 2026-02-08 |

### cs.CL - NLP/LLMs
| # | Title | Authors | Date |
|---|-------|---------|------|

### Abstracts

**[Paper Title](url)** - cs.AI
> First 200 chars of abstract...
```

## Notes

- cs.CL is key for LLM papers
- cs.AI for general AI/agent papers
- Sort by submittedDate for newest
