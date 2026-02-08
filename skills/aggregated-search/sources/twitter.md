# Twitter/X Search

Search Twitter for real-time discussions.

## Official API (Paid)

Requires Twitter API v2 access ($100/month minimum).

```bash
curl -s "https://api.twitter.com/2/tweets/search/recent?query={keyword}&max_results=100" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN" | \
  jq '.data[] | {
    text: .text,
    id: .id,
    url: ("https://twitter.com/i/web/status/" + .id)
  }'
```

## Alternative: Nitter (Free)

Use Nitter instances for public tweets:

```
WebFetch: https://nitter.net/search?f=tweets&q={keyword}
Prompt: Extract tweets with author, text, date, likes, retweets. Return as markdown.
```

## Nitter Instances

| Instance | URL |
|----------|-----|
| nitter.net | nitter.net |
| nitter.it | nitter.it |
| nitter.cz | nitter.cz |

## Search Operators

| Operator | Example | Description |
|----------|---------|-------------|
| from: | from:elonmusk | Tweets from user |
| to: | to:OpenAI | Replies to user |
| filter:links | filter:links | Only with links |
| min_faves: | min_faves:100 | Min likes |
| min_retweets: | min_retweets:50 | Min retweets |
| since: | since:2026-01-01 | After date |
| until: | until:2026-02-08 | Before date |

## Influential AI Accounts

| Account | Focus |
|---------|-------|
| @OpenAI | OpenAI official |
| @AnthropicAI | Anthropic |
| @GoogleAI | Google AI |
| @ylecun | Yann LeCun |
| @kaboris | Boris Dayma |
| @_akhaliq | AI paper digest |

## Output Format

```markdown
## Twitter/X

| # | Author | Tweet | Likes | RT | Date |
|---|--------|-------|-------|----|----- |
| 1 | @user | Text... | 500 | 100 | 2026-02-08 |

### Trending Hashtags
- #AI (1000 tweets)
- #LLM (500 tweets)
```

## Notes

- Official API is expensive
- Nitter may have availability issues
- Consider using Tavily for Twitter content
