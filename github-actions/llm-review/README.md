# LLM Code Review GitHub Actions

PR 自动代码审查，通过 LiteLLM（OpenAI 兼容接口）调用大模型。

## 文件说明

| 文件 | 功能 |
|------|------|
| `workflows/llm-review.yml` | LLM 代码审查 |
| `workflows/ci.yml` | 代码质量检查（black / flake8 / pytest） |
| `workflows/security.yml` | 安全扫描（gitleaks / pip-audit） |
| `scripts/llm_review.py` | 审查脚本 |

这些文件是模板，需要复制到目标仓库的 `.github/` 目录下使用。

## 使用方法

1. 复制文件到目标项目：
```bash
mkdir -p <project>/.github/workflows <project>/.github/scripts
cp workflows/* <project>/.github/workflows/
cp scripts/* <project>/.github/scripts/
```

2. 配置 GitHub Secrets：
   - `LITELLM_BASE_URL`（必填）: LiteLLM / OpenAI 兼容 API 地址，例如 `https://litellm.example.com/v1`。未设置或为空时审查直接失败，没有默认地址
   - `LITELLM_API_KEY`（必填）: API Key
   - `LITELLM_MODEL`（可选）: 模型名，默认 `qwen3-coder-480b`

3. **先把 workflow 和脚本合并到默认分支**，之后创建的 PR 会自动触发审查（`opened` / `synchronize` / `reopened`）。

4. 按项目实际情况调整 `ci.yml` 顶部的 `PYTHON_PATHS` / `REQUIREMENTS_FILE`，以及 `security.yml` 顶部的 `REQUIREMENTS_FILES`（默认检查整个仓库 `.` 和 `requirements.txt`）。

## 安全设计

- **审查脚本只从 PR 的 base commit 读取**：workflow 把 base commit 的 `.github/scripts` 单独 checkout 到 `trusted/` 并从那里运行，PR 里对 `llm_review.py` 的修改不会被执行（合并后才生效），避免 PR 篡改脚本窃取 `LITELLM_API_KEY`。
- PR head 只 checkout 到 `pr/` 用于计算 `git diff base...head`，其中的代码不会被执行；所有 checkout 都设置 `persist-credentials: false`。
- **Fork 仓库的 PR 会被跳过**：`pull_request` 事件下 GitHub 不向 fork PR 提供 secrets，审查无法运行。
- 防提示注入：PR 标题、描述和 diff 用标签隔离并在 system prompt 中声明为不可信数据；输出中的 `@提及` 会被转义，不会 ping 任何人；输出有长度上限，并标注为自动生成。
- 第三方 Action 固定到完整 commit SHA（注释中标明版本）。

## 行为说明

- diff 超过 50000 字符时按行截断，并在评论中注明只审查了前面一部分（可用环境变量 `MAX_DIFF_CHARS` 调整）。
- 评论通过隐藏标记 `<!-- llm-review-bot -->` 识别，每次推送更新同一条评论而不是新建。
- 审查失败（接口报错、返回为空、缺少配置等）时，脚本以非零退出码结束，job 显示失败，PR 上只会留下一条“review could not run”的简短提示，详细原因见 workflow 日志。
- 同一个 PR 有新推送时会取消正在运行的旧审查。

## 支持的模型

通过 LiteLLM 可使用网关上配置的任意模型（模型名以你的 LiteLLM 配置为准），例如：
- `qwen3-coder-480b`（默认，代码专用）
- `claude-sonnet-5`
- `claude-opus-5-5`
- `mistral-large-3`
- 等等
