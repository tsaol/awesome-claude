# Chinese Tech Sources

中文科技媒体数据源。

## Sites List

| 站点 | URL | 类型 |
|------|-----|------|
| 36氪 | 36kr.com | 创投科技 |
| 少数派 | sspai.com | 数码效率 |
| InfoQ | infoq.cn | 技术社区 |
| 掘金 | juejin.cn | 开发者 |
| CSDN | csdn.net | 技术博客 |
| 知乎 | zhihu.com | 问答 |
| 机器之心 | jiqizhixin.com | AI媒体 |
| 量子位 | qbitai.com | AI媒体 |

## 36氪

```
WebFetch: https://36kr.com/search/articles/{keyword}
Prompt: 提取文章标题、链接、日期、摘要，返回 markdown 表格。
```

## 少数派

```
WebFetch: https://sspai.com/search/article?q={keyword}
Prompt: 提取文章标题、链接、日期，返回 markdown 表格。
```

## 掘金 API

```bash
curl -s "https://api.juejin.cn/search_api/v1/search" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "key_word": "{keyword}",
    "search_type": 2,
    "cursor": "0",
    "limit": 20,
    "sort_type": 0
  }' | jq '.data[] | {
    title: .title,
    url: ("https://juejin.cn/post/" + .id),
    author: .author.name,
    views: .view_count,
    likes: .digg_count
  }'
```

## 机器之心

```
WebFetch: https://www.jiqizhixin.com/search?keywords={keyword}
Prompt: 提取文章标题、链接、日期、摘要。
```

## 知乎

```
WebFetch: https://www.zhihu.com/search?type=content&q={keyword}
Prompt: 提取问题标题、链接、回答数、关注数。
```

## Output Format

```markdown
## 中文科技源

### 36氪
| # | 标题 | 日期 |
|---|------|------|
| 1 | [标题](url) | 2026-02-08 |

### 机器之心
| # | 标题 | 日期 |
|---|------|------|
| 1 | [标题](url) | 2026-02-08 |

### 掘金
| # | 标题 | 作者 | 点赞 |
|---|------|------|------|
| 1 | [标题](url) | @author | 500 |
```

## Notes

- 部分站点可能需要处理反爬
- 知乎需登录查看完整内容
- 建议配合 Tavily 使用
