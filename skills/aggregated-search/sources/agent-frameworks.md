# Agent Framework Blogs

Official blogs from AI agent framework maintainers.

## Sources

| Framework | Blog URL | Focus |
|-----------|----------|-------|
| LangChain | blog.langchain.dev | Agent orchestration |
| LlamaIndex | llamaindex.ai/blog | RAG & data agents |
| Semantic Kernel | devblogs.microsoft.com/semantic-kernel | Microsoft agent SDK |
| CrewAI | crewai.com/blog | Multi-agent systems |
| AutoGen | microsoft.github.io/autogen/blog | Multi-agent (MS) |
| Haystack | haystack.deepset.ai/blog | RAG pipelines |

## Search Instructions

### LangChain Blog
```
WebFetch: https://blog.langchain.dev/
Prompt: Find articles related to {keyword}. Extract title, date, URL, summary.
```

### LlamaIndex Blog
```
WebFetch: https://www.llamaindex.ai/blog
Prompt: Find articles related to {keyword}. Extract title, date, URL.
```

### Semantic Kernel Blog
```
WebFetch: https://devblogs.microsoft.com/semantic-kernel/
Prompt: Find articles related to {keyword}. Extract title, date, URL.
```

### CrewAI Blog
```
WebFetch: https://www.crewai.com/blog
Prompt: Find articles related to {keyword}. Extract title, date, URL.
```

## GitHub Releases (Alternative)

Check releases for framework updates:
```bash
gh api repos/langchain-ai/langchain/releases --jq '.[0:5] | .[] | {tag: .tag_name, date: .published_at, notes: .body[0:100]}'
gh api repos/run-llama/llama_index/releases --jq '.[0:5] | .[] | {tag: .tag_name, date: .published_at}'
gh api repos/joaomdmoura/crewAI/releases --jq '.[0:5] | .[] | {tag: .tag_name, date: .published_at}'
```

## Output Format

```markdown
## Agent Frameworks

### LangChain
| # | Title | Date |
|---|-------|------|
| 1 | [Title](url) | 2026-02-08 |

### LlamaIndex
| # | Title | Date |
|---|-------|------|

### CrewAI
| # | Title | Date |
|---|-------|------|
```
