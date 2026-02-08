# Cloud Platform AI Blogs

AI/ML blogs from major cloud providers.

## AWS

| Blog | URL | Focus |
|------|-----|-------|
| AWS Machine Learning | aws.amazon.com/blogs/machine-learning | ML services |
| AWS AI | aws.amazon.com/blogs/ai | AI announcements |
| AWS News | aws.amazon.com/blogs/aws | General AWS |
| AWS Compute | aws.amazon.com/blogs/compute | Lambda, EC2 |
| AWS Developer | aws.amazon.com/blogs/developer | Dev tools |

### AWS Search
```
WebFetch: https://aws.amazon.com/blogs/machine-learning/
Prompt: Find articles related to {keyword}. Extract title, date, URL.
```

```
WebFetch: https://aws.amazon.com/blogs/ai/
Prompt: Find articles related to {keyword}. Extract title, date, URL.
```

## Google Cloud

| Blog | URL | Focus |
|------|-----|-------|
| Google Cloud AI | cloud.google.com/blog/products/ai-machine-learning | Vertex AI, etc |
| Google Cloud Blog | cloud.google.com/blog | General GCP |

### GCP Search
```
WebFetch: https://cloud.google.com/blog/products/ai-machine-learning
Prompt: Find articles related to {keyword}. Extract title, date, URL.
```

## Azure

| Blog | URL | Focus |
|------|-----|-------|
| Azure AI Blog | azure.microsoft.com/en-us/blog/tag/azure-ai/ | Azure AI services |
| Azure Blog | azure.microsoft.com/en-us/blog/ | General Azure |

### Azure Search
```
WebFetch: https://azure.microsoft.com/en-us/blog/tag/azure-ai/
Prompt: Find articles related to {keyword}. Extract title, date, URL.
```

## Output Format

```markdown
## Cloud AI Blogs

### AWS
| # | Title | Source | Date |
|---|-------|--------|------|
| 1 | [Title](url) | ML Blog | 2026-02-08 |

### Google Cloud
| # | Title | Date |
|---|-------|------|

### Azure
| # | Title | Date |
|---|-------|------|
```
