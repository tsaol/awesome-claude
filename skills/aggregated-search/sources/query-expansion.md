# Query Expansion

Expand search keywords to include related terms for comprehensive coverage.

## Strategy

Before searching, expand the original keyword into related terms:

```
Original: "agentic commerce"
    ↓
Expanded:
  - agentic commerce (original)
  - AI shopping agent
  - conversational commerce
  - e-commerce AI assistant
  - autonomous shopping
  - AI-powered retail
  - shopping copilot
  - LLM ecommerce
```

## LLM Expansion Prompt

Use this prompt to generate related terms:

```
Given the search keyword: "{keyword}"

Generate exactly 4 related search terms (5 total including original).

Requirements:
1. Include synonyms and alternative phrasings
2. Prioritize high-relevance terms only
3. Include 1 Chinese term if applicable
4. Keep terms specific and searchable

Output format (one term per line, max 4):
- term1
- term2
- term3
- term4
```

**IMPORTANT:** Maximum 5 terms total (1 original + 4 expanded). Quality over quantity.

## Example Expansions (Max 5)

### "agentic commerce"
```
- agentic commerce (original)
- AI shopping agent
- conversational commerce
- e-commerce AI assistant
- 智能购物 (Chinese)
```

### "RAG"
```
- RAG (original)
- retrieval augmented generation
- vector search LLM
- semantic retrieval
- 检索增强生成 (Chinese)
```

### "AI agent"
```
- AI agent (original)
- autonomous agent
- LLM agent
- agentic AI
- 智能体 (Chinese)
```

## Implementation

### Step 1: Generate Expanded Terms
```python
# Pseudo-code for expansion
expanded_terms = llm.expand(original_keyword)
# Returns: ["term1", "term2", "term3", ...]
```

### Step 2: Build Search Queries
For each source, construct queries:
```
GitHub: "term1 OR term2 OR term3"
HN: Search each term separately, merge results
Tavily: Use original + top 2 expanded terms
```

### Step 3: Merge & Deduplicate
```python
all_results = []
for term in expanded_terms:
    results = search_all_sources(term)
    all_results.extend(results)
deduplicated = deduplicate_by_url_and_title(all_results)
```

## Query Templates

### GitHub
```bash
gh api search/repositories -f q="{term1} OR {term2} OR {term3}"
```

### Hacker News
```bash
# Search each term, HN doesn't support OR
for term in terms:
    curl "https://hn.algolia.com/api/v1/search?query={term}"
```

### Tavily
```json
{
  "query": "{original} {expanded_term1} {expanded_term2}",
  "search_depth": "advanced"
}
```

## Predefined Expansions

For common AI topics, use these predefined expansions:

### AI/ML Topics
| Original | Expansions |
|----------|------------|
| LLM | large language model, GPT, Claude, 大语言模型 |
| RAG | retrieval augmented generation, vector search, 检索增强 |
| agent | AI agent, autonomous agent, 智能体 |
| fine-tuning | fine tune, PEFT, LoRA, 微调 |
| embedding | vector embedding, semantic embedding, 向量 |

### Commerce Topics
| Original | Expansions |
|----------|------------|
| e-commerce | ecommerce, online shopping, 电商 |
| retail | shopping, store, 零售 |
| recommendation | personalization, suggest, 推荐 |

## Output

Include expansion info in aggregated results:

```markdown
# Aggregated Search: {original_keyword}

**Expanded Terms:** {term1}, {term2}, {term3}...
**Sources:** 15 sources searched
**Results:** 200 unique items
```
