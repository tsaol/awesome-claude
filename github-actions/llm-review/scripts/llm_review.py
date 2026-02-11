#!/usr/bin/env python3
"""
AI Code Review via LiteLLM
Analyzes PR diff and generates review comments
Default model: qwen3-coder-480b
"""

import os
from openai import OpenAI

def get_client():
    """Create LiteLLM client (OpenAI compatible)"""
    return OpenAI(
        base_url=os.environ.get('LITELLM_BASE_URL', 'https://litellm.xcaoliu.com/v1'),
        api_key=os.environ.get('LITELLM_API_KEY', '')
    )

def read_diff():
    """Read PR diff file"""
    with open('pr_diff.txt', 'r') as f:
        diff = f.read()
    # Truncate if too long
    max_chars = 50000
    if len(diff) > max_chars:
        diff = diff[:max_chars] + "\n\n... (diff truncated)"
    return diff

def review_code(diff: str, pr_title: str, pr_body: str) -> str:
    """Call LLM via LiteLLM to review code"""
    client = get_client()

    prompt = f"""You are a senior code reviewer. Review the following Pull Request.

## PR Title
{pr_title}

## PR Description
{pr_body or 'No description provided'}

## Code Changes (diff)
```diff
{diff}
```

## Review Instructions
Please review the code for:
1. **Security Issues**: Hardcoded secrets, SQL injection, XSS, etc.
2. **Code Quality**: Readability, maintainability, best practices
3. **Bugs**: Logic errors, edge cases, potential runtime errors
4. **Performance**: Inefficient code, unnecessary operations

## Output Format
Provide your review in the following format:

### Summary
(Brief overall assessment)

### Security
(Any security concerns, or "No issues found")

### Code Quality
(Suggestions for improvement)

### Potential Bugs
(Any bugs or edge cases)

### Recommendations
(Actionable suggestions)

Keep the review concise and actionable. Use Chinese for the review content.
"""

    response = client.chat.completions.create(
        model=os.environ.get('LITELLM_MODEL', 'qwen3-coder-480b'),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096
    )

    return response.choices[0].message.content

def main():
    print("Starting LLM Code Review...")

    # Read inputs
    diff = read_diff()
    pr_title = os.environ.get('PR_TITLE', 'Unknown')
    pr_body = os.environ.get('PR_BODY', '')

    print(f"PR Title: {pr_title}")
    print(f"Diff length: {len(diff)} chars")

    # Get review
    try:
        review = review_code(diff, pr_title, pr_body)
    except Exception as e:
        review = f"Review failed: {str(e)}"
        print(f"Error: {e}")

    # Format output
    model = os.environ.get('LITELLM_MODEL', 'qwen3-coder-480b')
    output = f"""## LLM Code Review

{review}

---
*Reviewed by {model} via LiteLLM*
"""

    # Write result
    with open('review_result.md', 'w') as f:
        f.write(output)

    print("Review completed. Output saved to review_result.md")

if __name__ == '__main__':
    main()
