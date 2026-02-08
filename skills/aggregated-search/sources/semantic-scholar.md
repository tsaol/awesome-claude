# Semantic Scholar

AI-powered academic search engine by Allen Institute for AI (AI2).

## Overview

| 特性 | 说明 |
|------|------|
| **官网** | https://www.semanticscholar.org |
| **API 文档** | https://api.semanticscholar.org |
| **论文数量** | 2 亿+ 篇 |
| **数据源** | ArXiv, PubMed, ACL, IEEE, Springer 等 |
| **特色** | AI 驱动的语义搜索、引用分析、TLDR 摘要 |

## API Endpoints

| Endpoint | 用途 |
|----------|------|
| `/paper/search` | 搜索论文 |
| `/paper/{paper_id}` | 获取论文详情 |
| `/paper/{paper_id}/citations` | 获取引用该论文的论文 |
| `/paper/{paper_id}/references` | 获取该论文引用的论文 |
| `/author/search` | 搜索作者 |
| `/author/{author_id}` | 获取作者详情 |
| `/recommendations` | 论文推荐 |

## Search Papers

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={keyword}&limit=50&fields=title,url,year,authors,citationCount,abstract,venue,openAccessPdf" | \
  jq '.data[] | {
    title: .title,
    url: .url,
    year: .year,
    citations: .citationCount,
    authors: [.authors[].name] | join(", "),
    venue: .venue,
    pdf: .openAccessPdf.url,
    abstract: .abstract[:200]
  }'
```

## Search with Filters

### Filter by Year
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={keyword}&year=2024-2026&limit=50&fields=title,year,citationCount"
```

### Filter by Venue (Conference/Journal)
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={keyword}&venue=NeurIPS,ICML,ACL&limit=50&fields=title,venue,year"
```

### Filter by Open Access
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={keyword}&openAccessPdf&limit=50&fields=title,openAccessPdf"
```

### Filter by Fields of Study
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={keyword}&fieldsOfStudy=Computer Science&limit=50&fields=title,fieldsOfStudy"
```

## Get Paper Details

```bash
# By Semantic Scholar ID
curl -s "https://api.semanticscholar.org/graph/v1/paper/649def34f8be52c8b66281af98ae884c09aef38b?fields=title,abstract,authors,citationCount,references"

# By ArXiv ID
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2210.03629?fields=title,abstract,citationCount"

# By DOI
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:10.18653/v1/2023.acl-long.1?fields=title,abstract"
```

## Get Citations

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?limit=50&fields=title,year,citationCount"
```

## Search Authors

```bash
curl -s "https://api.semanticscholar.org/graph/v1/author/search?query=Yann%20LeCun&fields=name,hIndex,paperCount,citationCount"
```

## Available Fields

### Paper Fields
| Field | Description |
|-------|-------------|
| `paperId` | Semantic Scholar ID |
| `title` | Paper title |
| `abstract` | Abstract text |
| `year` | Publication year |
| `authors` | Author list |
| `citationCount` | Number of citations |
| `referenceCount` | Number of references |
| `venue` | Conference/Journal |
| `url` | Semantic Scholar URL |
| `openAccessPdf` | PDF link if available |
| `fieldsOfStudy` | Research fields |
| `tldr` | AI-generated TLDR summary |
| `embedding` | Paper embedding vector |

### Author Fields
| Field | Description |
|-------|-------------|
| `authorId` | Author ID |
| `name` | Author name |
| `hIndex` | h-index |
| `paperCount` | Number of papers |
| `citationCount` | Total citations |

## Output Format

```markdown
## Semantic Scholar Papers

| # | Title | Year | Citations | Venue |
|---|-------|------|-----------|-------|
| 1 | [Title](url) | 2025 | 150 | NeurIPS |
| 2 | [Title](url) | 2025 | 100 | ICML |

### Highly Cited
1. **[Paper Title](url)** - 500 citations
   > Abstract preview...

### With PDF
1. [Paper Title](pdf_url) - Open Access
```

## Rate Limits

| Tier | Limit | Notes |
|------|-------|-------|
| 无 API Key | 100 requests / 5 min | 适合测试 |
| 有 API Key | 1 request / second | 免费申请 |
| Partner | 更高 | 需联系 AI2 |

### 申请 API Key
1. 访问 https://www.semanticscholar.org/product/api
2. 点击 "Request API Key"
3. 填写申请表单
4. 通常 1-2 天审批

## vs ArXiv

| 对比 | Semantic Scholar | ArXiv |
|------|------------------|-------|
| 数据源 | 多源聚合 | 仅 ArXiv |
| API 稳定性 | ✅ 稳定 | ⚠️ 不稳定 |
| 引用数据 | ✅ 有 | ❌ 无 |
| TLDR 摘要 | ✅ AI 生成 | ❌ 无 |
| 作者搜索 | ✅ 支持 | ❌ 不支持 |
| 推荐系统 | ✅ 有 | ❌ 无 |

## Notes

- 免费且无需认证即可使用
- 包含 ArXiv 论文 (通过 `arXiv:` 前缀查询)
- 引用数据每周更新
- TLDR 摘要由 AI 自动生成
- 推荐作为 ArXiv 的稳定替代方案
