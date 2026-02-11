# LLM Code Review GitHub Actions

PR 自动代码审查，使用 LiteLLM 调用大模型。

## 文件说明

| 文件 | 功能 |
|------|------|
| `workflows/llm-review.yml` | LLM 代码审查 |
| `workflows/ci.yml` | 代码质量检查 |
| `workflows/security.yml` | 安全扫描 |
| `scripts/llm_review.py` | 审查脚本 |

## 使用方法

1. 复制文件到目标项目：
```bash
cp -r workflows/* <project>/.github/workflows/
cp -r scripts/* <project>/.github/scripts/
```

2. 配置 GitHub Secrets：
   - `LITELLM_BASE_URL`: LiteLLM API 地址
   - `LITELLM_API_KEY`: API Key
   - `LITELLM_MODEL`: 模型名（可选，默认 qwen3-coder-480b）

3. 创建 PR 即可自动触发审查

## 支持的模型

通过 LiteLLM 支持多种模型：
- `qwen3-coder-480b` (默认，代码专用)
- `claude-sonnet-4.5`
- `mistral-large-3`
- 等等

## 配置示例

LiteLLM:
- URL: `https://litellm.xcaoliu.com/v1`
- 支持 17 个模型
