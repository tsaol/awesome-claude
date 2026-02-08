# AI Labs Official Blogs

Official blogs from major AI research labs.

## Sources

| Lab | Blog URL | RSS/Feed |
|-----|----------|----------|
| OpenAI | openai.com/blog | openai.com/blog/rss.xml |
| Anthropic | anthropic.com/news | - |
| Google AI | ai.googleblog.com | ai.googleblog.com/feeds/posts/default |
| DeepMind | deepmind.google/blog | - |
| Meta AI | ai.meta.com/blog | - |
| Microsoft Research | microsoft.com/en-us/research/blog | - |
| Hugging Face | huggingface.co/blog | - |

## Search Instructions

### OpenAI Blog
```
WebFetch: https://openai.com/blog
Prompt: Find articles related to {keyword}. Extract title, date, URL, summary.
```

### Anthropic News
```
WebFetch: https://www.anthropic.com/news
Prompt: Find articles related to {keyword}. Extract title, date, URL, summary.
```

### Google AI Blog
```
WebFetch: https://ai.googleblog.com/search?q={keyword}
Prompt: Extract blog post titles, dates, and URLs matching the search.
```

### DeepMind Blog
```
WebFetch: https://deepmind.google/discover/blog/
Prompt: Find articles related to {keyword}. Extract title, date, URL.
```

### Meta AI Blog
```
WebFetch: https://ai.meta.com/blog/
Prompt: Find articles related to {keyword}. Extract title, date, URL.
```

### Microsoft Research
```
WebFetch: https://www.microsoft.com/en-us/research/blog/
Prompt: Find articles related to {keyword}. Extract title, date, URL.
```

### Hugging Face Blog
```
WebFetch: https://huggingface.co/blog
Prompt: Find articles related to {keyword}. Extract title, date, URL.
```

## Output Format

```markdown
## AI Labs Official

### OpenAI
| # | Title | Date |
|---|-------|------|
| 1 | [Title](url) | 2026-02-08 |

### Anthropic
| # | Title | Date |
|---|-------|------|

### Google AI
| # | Title | Date |
|---|-------|------|

### DeepMind
| # | Title | Date |
|---|-------|------|
```
