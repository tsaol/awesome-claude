# Product Hunt Search

Search for new products and launches.

## Authentication Setup

Product Hunt API requires OAuth 2.0 authentication. Follow these steps to get your access token:

### Step 1: Create a Product Hunt Account

1. Sign up at [https://www.producthunt.com](https://www.producthunt.com) if you don't have an account

### Step 2: Register a Developer Application

1. Go to the API dashboard: [https://api.producthunt.com/v2/oauth/applications](https://api.producthunt.com/v2/oauth/applications)
2. Click "Add an Application"
3. Fill in the required fields:
   - **App Name**: Your application name
   - **Redirect URI**: `https://localhost:3000/` (for testing) or your actual callback URL
4. After creation, you'll receive:
   - **Client ID** (API Key)
   - **Client Secret** (API Secret)

### Step 3: Get Access Token

#### Option A: Developer Token (Recommended for Personal Use)

1. On your application page in the API dashboard, scroll to the bottom
2. Click "Generate Developer Token"
3. This token **does not expire** and is linked to your account
4. Use this token directly as `PRODUCTHUNT_TOKEN`

#### Option B: Client Credentials Flow (For Server Applications)

```bash
curl -X POST "https://api.producthunt.com/v2/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "grant_type": "client_credentials"
  }'
```

Response:
```json
{
  "access_token": "your_access_token_here",
  "token_type": "bearer",
  "scope": "public"
}
```

#### Option C: OAuth User Authentication (For User-Context Access)

1. Redirect user to authorize:
```
https://api.producthunt.com/v2/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=public+private
```

2. Exchange the authorization code for token:
```bash
curl -X POST "https://api.producthunt.com/v2/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uri": "YOUR_REDIRECT_URI",
    "code": "AUTHORIZATION_CODE",
    "grant_type": "authorization_code"
  }'
```

### Step 4: Set Environment Variable

```bash
export PRODUCTHUNT_TOKEN="your_access_token_here"
```

## GraphQL API

The API endpoint is: `https://api.producthunt.com/v2/api/graphql`

### Search Products by Topic

```bash
curl -s "https://api.producthunt.com/v2/api/graphql" \
  -H "Authorization: Bearer $PRODUCTHUNT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { posts(first: 50, topic: \"{keyword}\") { edges { node { name tagline url votesCount commentsCount thumbnail { url } } } } }"
  }' | jq '.data.posts.edges[].node'
```

### Get Today's Posts

```bash
curl -s "https://api.producthunt.com/v2/api/graphql" \
  -H "Authorization: Bearer $PRODUCTHUNT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { posts(first: 20) { edges { node { id name tagline url votesCount createdAt } } } }"
  }' | jq '.data.posts.edges[].node'
```

### Search Posts

```bash
curl -s "https://api.producthunt.com/v2/api/graphql" \
  -H "Authorization: Bearer $PRODUCTHUNT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query SearchPosts($query: String!) { posts(first: 20, query: $query) { edges { node { name tagline url votesCount } } } }",
    "variables": {"query": "{keyword}"}
  }' | jq '.data.posts.edges[].node'
```

## Rate Limits

- **GraphQL endpoint**: 6250 complexity points per 15 minutes
- **Other endpoints**: 450 requests per 15 minutes
- Check response headers for current usage:
  - `X-Rate-Limit-Limit`: Your limit for the 15-minute period
  - `X-Rate-Limit-Remaining`: Remaining quota
  - `X-Rate-Limit-Reset`: Seconds until reset

## Alternative: Search via WebFetch (No Auth Required)

If you don't need the API, you can scrape Product Hunt pages directly:

```
WebFetch: https://www.producthunt.com/search?q={keyword}
Prompt: Extract product names, taglines, upvotes, and URLs. Return as markdown table.
```

## Alternative: Search via Exa API

Exa API can search Product Hunt content without authentication:

```bash
curl -s "https://api.exa.ai/search" \
  -H "x-api-key: YOUR_EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{keyword} site:producthunt.com",
    "numResults": 20,
    "type": "auto",
    "contents": {"text": true}
  }' | jq '.results[] | {title, url, text}'
```

## Topics

| Topic | Slug |
|-------|------|
| Artificial Intelligence | artificial-intelligence |
| Developer Tools | developer-tools |
| Productivity | productivity |
| Marketing | marketing |
| SaaS | saas |
| Open Source | open-source |

## Browse Topics

```
WebFetch: https://www.producthunt.com/topics/artificial-intelligence
Prompt: Extract products with name, tagline, upvotes, and URL.
```

## Output Format

```markdown
## Product Hunt

| # | Product | Tagline | Upvotes | Comments |
|---|---------|---------|---------|----------|
| 1 | [Name](url) | AI-powered... | 1500 | 200 |
| 2 | [Name](url) | Build faster... | 800 | 100 |

### Trending in AI
1. **[Product](url)** - 1500 upvotes
   > Tagline description
```

## Troubleshooting

### 403 Forbidden Error

If you receive a 403 error:
1. Verify your access token is valid and not expired
2. Ensure the Authorization header format is correct: `Bearer YOUR_TOKEN`
3. Check if your application has the required scope
4. For client credentials tokens, scope is limited to "public" only

### Invalid Token

Developer tokens do not expire, but OAuth tokens may. Refresh or regenerate if needed.

## Resources

- **API Documentation**: [https://api.producthunt.com/v2/docs](https://api.producthunt.com/v2/docs)
- **GraphQL Reference**: [https://api.producthunt.com/v2/docs/graphql](https://api.producthunt.com/v2/docs)
- **API Explorer**: [https://ph-graph-api-explorer.herokuapp.com/](https://ph-graph-api-explorer.herokuapp.com/)
- **Rate Limits**: [https://api.producthunt.com/v2/docs/rate_limits/headers](https://api.producthunt.com/v2/docs/rate_limits/headers)

## Notes

- API requires authentication (see setup above)
- WebFetch works for basic browsing without auth
- Exa API is a good alternative for searching Product Hunt content
- Good for finding new tools and products
- Commercial use requires contacting Product Hunt directly
