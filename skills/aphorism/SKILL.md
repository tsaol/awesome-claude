---
name: aphorism
description: Aphorism (金句/随想) micro-post pipeline for Toutiao. Distills this week's news (whatsnew daily reports in S3) into structural insights, generates candidates with 3 models in parallel (Opus, Kimi K2.5, DeepSeek V3.2), then critic, refiner, de-AI, and publishes micro-posts only after user confirmation. Requires the external toutiao repo (TOUTIAO_DIR).
---

# Aphorism - 金句/随想微头条

从本周热点事件出发，通过多模型竞争生成 + Opus 评审精修，产出 5-10 条锚定具体事件的金句（每条 1-3 句），发布为头条号微头条。

## Usage

```
/aphorism [options]
```

**Examples:**
```
/aphorism                  # 通用视角
/aphorism --sa             # AI 时代解决方案架构师视角（Step 2-SA）
/aphorism --no-publish     # 只生成，不发布
```

## Prerequisites（外部依赖）

本 skill 依赖外部仓库 **toutiao**（包含 PROMPT 文件、`.claude/agents/`、`config/` 和 `scripts/`），本仓库不包含这些文件。通过环境变量 `TOUTIAO_DIR` 指定其位置，默认 `~/code/toutiao`：

```bash
export TOUTIAO_DIR="$HOME/code/toutiao"   # 按实际位置修改
```

还需要：
- `$TOUTIAO_DIR/eval/`：`invoke_model.py` 依赖的 Bedrock 客户端和模型配置。该目录被 gitignore，clone 后不存在，可从 git 历史恢复：
  ```bash
  cd "$TOUTIAO_DIR" && git archive "$(git log --all --format=%H -1 -- eval/clients.py)^" eval | tar -x
  ```
- 一个装了 `boto3` 的 Python，以及 AWS 凭证：能调用 Bedrock（us-east-1）上 Opus / Kimi K2.5 / DeepSeek V3.2，能读 `s3://cls-whatsnew`（whatsnew 日报，可用 `WHATSNEW_S3_BUCKET` 改）。

**开始执行前先检查**，缺失时立即停止并清晰提示用户，不要凭空臆造流程：

```bash
TOUTIAO_DIR="${TOUTIAO_DIR:-$HOME/code/toutiao}"
[ -f "$TOUTIAO_DIR/PROMPT-aphorism.md" ] || { echo "✗ 未找到 $TOUTIAO_DIR/PROMPT-aphorism.md：本 skill 需要外部 toutiao 仓库，请 clone 后设置 TOUTIAO_DIR"; exit 1; }
[ -f "$TOUTIAO_DIR/eval/clients.py" ] || { echo "✗ 缺少 $TOUTIAO_DIR/eval/：invoke_model.py 无法运行，按上面的命令从 git 历史恢复"; exit 1; }
PY=$(for p in python python3; do command -v $p >/dev/null && $p -c "import boto3" 2>/dev/null && { command -v $p; break; }; done)
[ -n "$PY" ] || { echo "✗ 没有装了 boto3 的 Python"; exit 1; }
```

## Pipeline

**执行此 skill 时，必须读取并严格按照以下 PROMPT 文件执行：**

```
$TOUTIAO_DIR/PROMPT-aphorism.md
```

### 执行适配（PROMPT 里的路径是作者机器上的，必须替换）

- **工作目录**：所有命令都在 `$TOUTIAO_DIR` 下执行（`cd "$TOUTIAO_DIR"`）。PROMPT 里的 `.claude/agents/...`、`config/...`、`articles/...` 都是相对这个目录的。
- **路径**：把 `/home/ubuntu/codes/toutiao` 一律替换为 `$TOUTIAO_DIR`。
- **Python**：把 `python3` 替换为上面检查出的 `$PY`。
- **日志**：`scripts/log.py` 收到相对路径时会拼到 `~/codes/toutiao/articles`，所以必须传绝对路径：`"$PY" scripts/log.py "$TOUTIAO_DIR/$ARTICLE_DIR" <step> <status> "<message>"`。
- **S3 日报不足 5 篇时（Step 1.5）**：按 PROMPT 改用 WebSearch 搜集最近 7 天 10-20 条热点新闻（科技、AI、商业、社会各覆盖一些），每条写标题、日期、来源链接和 2-3 句摘要，存到 `process/weekly_news.md`，然后照常执行 Step 1.6。在 `pipeline.log` 记录 `⚠ S3 日报不足，已改用 WebSearch`。
- **`--sa`**：用 Step 2-SA 替代 Step 2。
- **某个模型调用失败**：按 PROMPT 规定用剩余模型继续，并记录日志。

### 流程概览

```
Step 1:   创建目录 articles/YYYYMMDD-HHMMSS-aphorism/
Step 1.5: fetch_s3_weekly.py (不足 5 篇则 WebSearch) → process/weekly_news.md
Step 1.6: aphorism-distiller(Opus)            → process/weekly_insights.md (5-8 条洞察+事件锚点)
Step 2:   aphorism-gen x3 并行 (Opus/Kimi/DeepSeek) → raw/candidates.md (24-36 条)
Step 3:   aphorism-critic(Opus, 两批并行)      → process/critique.md (PASS/REFINE/KILL)
Step 4:   aphorism-refiner(Opus)              → output/v1_draft.md
Step 5:   toutiao-deai(Opus)                  → output/v3_final.md
Step 6:   展示给用户 → 用户选择 → publish_micro_post
```

### Agents (in $TOUTIAO_DIR/.claude/agents/，通过 invoke_model.py 的 --system-prompt 使用)

| Step | Agent | Role |
|------|-------|------|
| 1.6 | aphorism-distiller | 新闻 → 结构性洞察（每条带事件锚点） |
| 2 | aphorism-gen / aphorism-gen-sa | 按模式库生成候选金句 |
| 3 | aphorism-critic | 5 维度逐条评审，宁缺毋滥 |
| 4 | aphorism-refiner | 字词级精修 |
| 5 | toutiao-deai | 去 AI 痕迹 |

## 发布（Step 6）

- **必须先把 `output/v3_final.md` 的全部金句展示给用户，由用户选择发布哪几条、何时发布。** 金句代表个人品牌，绝不自动发布。
- 发布用 `toutiao-mcp` 的 `publish_micro_post` 工具。如果该 MCP 没有配置，停在展示这一步，告诉用户终稿路径。
- `--no-publish` 时只展示，不发布。

## Output Structure

```
$TOUTIAO_DIR/articles/YYYYMMDD-HHMMSS-aphorism/
├── raw/
│   ├── candidates_opus.md
│   ├── candidates_kimi.md
│   ├── candidates_deepseek.md
│   └── candidates.md       # 汇总候选
├── output/
│   ├── v1_draft.md         # 精修后
│   └── v3_final.md         # 最终版
└── process/
    ├── pipeline.log
    ├── weekly_news.md
    ├── weekly_insights.md
    ├── critique.md
    └── step*_input.md
```

## Key Rules

- 所有步骤的详细规则在 PROMPT-aphorism.md 中定义
- 每条金句必须标注 `[事件锚点: X]`，至少覆盖 5 个不同事件/趋势
- 每条金句必须有具象比喻或画面，非程序员也能读懂
- 存活 (PASS+REFINE) < 5 条时回到 Step 2 重试，最多 1 次
- 纯文字，无图片
