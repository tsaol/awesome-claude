# Chinese AI Media (中文 AI 媒体)

High-quality Chinese AI/tech media sources.

## Sources

| 媒体 | URL | 类型 |
|------|-----|------|
| 机器之心 | jiqizhixin.com | AI 深度报道 |
| 新智元 | 36kr.com/user/51467501 | AI 资讯 |
| 量子位 | qbitai.com | AI 资讯 |
| 钛媒体 AI | tmtpost.com/tag/ai | 科技财经 |
| 36氪 AI | 36kr.com/information/ai | 创投科技 |
| InfoQ AI | infoq.cn/topic/ai | 技术社区 |
| AI 科技评论 | leiphone.com/category/ai | 雷锋网 AI |

## Search Instructions

### 机器之心
```
WebFetch: https://www.jiqizhixin.com/search?keywords={keyword}
Prompt: 提取文章标题、链接、日期、摘要，返回 markdown 表格。
```

### 量子位
```
WebFetch: https://www.qbitai.com/?s={keyword}
Prompt: 提取文章标题、链接、日期，返回 markdown 表格。
```

### 钛媒体
```
WebFetch: https://www.tmtpost.com/search/{keyword}
Prompt: 提取文章标题、链接、日期，返回 markdown 表格。
```

### 36氪
```
WebFetch: https://36kr.com/search/articles/{keyword}
Prompt: 提取文章标题、链接、日期、摘要，返回 markdown 表格。
```

### InfoQ
```
WebFetch: https://www.infoq.cn/search?keywords={keyword}
Prompt: 提取文章标题、链接、日期，返回 markdown 表格。
```

### 雷锋网 AI
```
WebFetch: https://www.leiphone.com/search?s={keyword}
Prompt: 提取文章标题、链接、日期，返回 markdown 表格。
```

## Output Format

```markdown
## 中文 AI 媒体

### 机器之心
| # | 标题 | 日期 |
|---|------|------|
| 1 | [标题](url) | 2026-02-08 |

### 量子位
| # | 标题 | 日期 |
|---|------|------|

### 36氪
| # | 标题 | 日期 |
|---|------|------|

### 钛媒体
| # | 标题 | 日期 |
|---|------|------|
```

## Notes

- 机器之心: 最专业的 AI 媒体，深度报道
- 量子位: 更新快，覆盖广
- 36氪: 创投视角，商业分析
- 钛媒体: 科技财经综合
