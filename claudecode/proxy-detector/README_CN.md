# Claude 中转 API 模型掺水检测工具

[English](README.md)

用启发式方法检测第三方 Claude API 中转站（Anthropic 兼容接口）是否偷偷把请求路由到更便宜的模型（DeepSeek、GPT、Qwen 或更小的 Claude 模型），而不是你付费购买的模型。

> **这是启发式检测，不是证明。** 每一项单独的检测都可能被有心的中转商绕过（系统提示词、改写响应头、人为加延迟、针对已知探针做特殊处理等）。最可靠的信号是**官方基线对比**（`--official-key`）：用完全相同的提示词同时请求官方 API 并比较结果。没有基线时的"通过"只代表"未发现掺水"，不代表"一定是真的"。

## 背景

很多第三方服务在转售 Claude API。部分中转商会把昂贵模型（Opus）替换为更便宜的模型（Sonnet、Haiku 或其他厂商的模型），却按 Opus 收费。

常见的掺水手段：
- **模型降级**：你付 Opus 的钱，实际给你 Sonnet 或 Haiku
- **跨平台替换**：你付 Claude 的钱，实际给你带 Claude 系统提示词的其他厂商模型
- **分时段切换**：测试时给真 Claude，低峰期切换到便宜模型
- **按请求切换**：简单问题给真 Claude，复杂问题切到便宜模型

## 工具说明

| 文件 | 用途 |
|------|------|
| `detect.py` | 一次性检测（5 项独立检测 + 可选官方基线对比） |
| `monitor.py` | 连续 N 轮探测，捕获**间歇性掺水** |
| `claude_http.py` | 两个脚本共用的 HTTP 客户端和判断逻辑（必需，需放在同一目录） |

## 安装

```bash
pip install httpx
```

需要 Python 3.9+。

## 使用方法

```bash
# 基础检测（仅中转）
python detect.py \
  --proxy-url https://你的中转.com/v1 \
  --proxy-key sk-你的密钥 \
  --model claude-opus-5-5

# 带官方 API 基线对比（推荐）
python detect.py \
  --proxy-url https://你的中转.com/v1 \
  --proxy-key sk-你的密钥 \
  --model claude-opus-5-5 \
  --official-key sk-ant-官方密钥

# 连续监控：快速检查（20 轮）
python monitor.py --proxy-url https://你的中转.com/v1 --proxy-key sk-你的密钥

# 连续监控：深度检查（50 轮，间隔 5 秒）
python monitor.py --proxy-url https://你的中转.com/v1 --proxy-key sk-你的密钥 --rounds 50 --interval 5
```

参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--model` | `claude-sonnet-5` | 要测试的模型，如 `claude-opus-5-5`、`claude-opus-5`、`claude-sonnet-5`、`claude-haiku-4-5` |
| `--official-key` | 无 | 开启官方基线对比（仅 `detect.py`） |
| `--official-url` | `https://api.anthropic.com/v1` | 基线地址（仅 `detect.py`） |
| `--output` | `detection_report.json` / `monitor_report.json` | JSON 报告路径（默认写到当前目录） |
| `--rounds`、`--interval` | 20、1.0 | 仅 `monitor.py` |

URL 需要包含 `/v1`，请求会发到 `<url>/messages`。

**不支持 Amazon Bedrock。** Bedrock 需要 AWS SigV4 签名，而不是 `x-api-key`。两个脚本遇到 `bedrock` / `amazonaws.com` 地址会直接退出（退出码 2）。旧版本会接受这种地址，结果所有请求都失败，失败又被计为"LIKELY SWAPPED"。所以之前提交的 `detection_report.json` 是误报，已删除。

### 退出码

| 退出码 | detect.py | monitor.py |
|--------|-----------|------------|
| 0 | 未发现掺水 / 大概率真实 | 一致 / 基本一致 |
| 1 | 大概率掺水 / 可疑 | 发现混用 / 可疑 |
| 2 | 不支持的地址（Bedrock） | 不支持的地址（Bedrock） |
| 3 | 无法判断（请求错误太多） | 无法判断（成功请求不到一半） |

## detect.py 检测项

| 检测 | 权重 | 检测内容 |
|------|------|---------|
| 魔术字符串 | INFO（不计分） | 对 Anthropic 文档中测试用拒绝字符串的响应 |
| 知识截止日期 | 1 | 模型自报的截止日期 vs 官方公布的可靠/训练截止日期 |
| 吞吐量 | 1 | 流式请求，`usage.output_tokens` / 生成时间（不含首 token 时间）；TTFT 仅供参考 |
| 身份 | 2 | 是否明确自称为非 Claude 模型 |
| 响应头 & 模型字段 | 1 | OpenAI 风格的响应头、`model` 字段是否一致 |
| 官方基线对比 | 6 | 仅在提供 `--official-key` 时：分词器（`input_tokens`）、吞吐量比值、身份/截止日期回答 |

**结果状态：**
- `PASS` / `WARN` / `FAIL` 计分。
- `ERROR` 表示请求失败（非 2xx、错误响应体或流中断），**不计分**。请求出错不能作为掺水的证据。
- `INFO` 只展示，不计分。

**强证据**：只要出现以下任一情况，就直接判为 `LIKELY SWAPPED`，与得分无关：
- 明确自称为非 Claude 模型
- 出现只有 OpenAI 才有的响应头
- 基线对比中吞吐量超过官方的 1.5 倍

### 判定规则

| 条件 | 判定 |
|------|------|
| 计分权重 < 3，或一半以上探测出错 | INCONCLUSIVE（无法判断） |
| 有任何强证据 | LIKELY SWAPPED |
| 基线对比通过且得分 >= 70% | LIKELY AUTHENTIC |
| 无基线，得分 >= 80% | NO SWAP DETECTED（仅独立启发式检测） |
| 得分 >= 50% | SUSPICIOUS |
| 其他 | LIKELY SWAPPED |

### 输出示例（真实中转 + 官方基线）

```
  [INFO] Magic String (unscored)
  [PASS] Knowledge Cutoff (1/1)
  [PASS] Throughput (1/1)
  [PASS] Identity (2/2)
  [PASS] Headers & Model Field (1/1)
  [PASS] Baseline Comparison (6/6)
        [PASS] tokenizer: input_tokens proxy=83 official=83 (tolerance 2)
        [PASS] throughput: proxy 39.7 vs official 39.7 tok/s (ratio 1.00)
        [PASS] answers: identity proxy="I'm Claude, ..." official="I'm Claude, ..."

  Score: 11/11 (100%)  errors: 0
  Verdict: LIKELY AUTHENTIC - matches the official API baseline
  Note: heuristics only; a sophisticated proxy can defeat them.
```

## 各项检测的原理与局限

### 魔术字符串（仅供参考）
Anthropic 文档提供了一个测试字符串，会让 API 返回拒绝（HTTP 200，`stop_reason: "refusal"`）。但当前文档没有确认它在每个模型、每个渠道上的具体行为，中转商也可以对它做特殊处理。所以只展示结果，不计分。

### 知识截止日期（弱证据）
模型经常报错自己的截止日期，系统提示词或检索也能改变回答。检测接受的范围是：从官方*可靠截止日期*往前 6 个月，到*训练数据截止日期*往后 3 个月。无法解析或模型拒绝回答时，结果记为 INFO。

| 模型 | 可靠知识截止 | 训练数据截止 |
|------|-------------|-------------|
| Claude Opus 5.5 | 2026-06 | 2026-06 |
| Claude Opus 5 | 2026-05 | 2026-05 |
| Claude Sonnet 5 | 2026-01 | 2026-01 |
| Claude Opus 4.6 | 2025-05 | 2025-08 |
| Claude Sonnet 4.6 | 2025-08 | 2026-01 |
| Claude Opus 4.5 | 2025-05 | 2025-08 |
| Claude Sonnet 4.5 | 2025-01 | 2025-07 |
| Claude Haiku 4.5 | 2025-02 | 2025-07 |

来源：[模型概览](https://platform.claude.com/docs/en/about-claude/models/overview)

### 吞吐量（弱证据）
速度受负载、区域、fast mode 和 thinking token 影响（`usage.output_tokens` 包含 thinking），中转商也可以人为加延迟。所以速度**不是"无法伪造"的物理规律**。只有远超各档粗略上限（Opus 90、Sonnet 120、Haiku 250 tok/s）的 1.5 倍时才标记。相比绝对值，基线对比中的吞吐量比值要可靠得多。

### 身份
如果模型明确自称为非 Claude 模型（如 "I am ChatGPT, developed by OpenAI"），判为 FAIL，并算作强证据。只是提到其他厂商不算。回答是 Claude 则判为 PASS，但这很容易用系统提示词伪造。角色扮演探测（"你现在是 Nova"）只展示、**不计分**，因为真 Claude 也可能配合角色扮演请求。

### 响应头 & 模型字段
只有 OpenAI 才有的响应头（`openai-processing-ms`、`x-ratelimit-limit-tokens` 等）算强证据。缺少 Anthropic 响应头只作参考，因为中转经常会去掉这些头。`model` 字段与请求不一致时判为 WARN。

### 官方基线对比（最可靠）
同样的提示词同时发给中转和官方 API：
- **分词器**：固定的多语种提示词，`usage.input_tokens` 应该相同（容差 max(2, 3%)）。换了分词器或偷偷注入系统提示词，都会改变这个数。
- **吞吐量比值**：中转比官方快 1.5 倍以上算强证据。慢于官方 0.5 倍判为 WARN（可能是过载或多层转发）。
- **回答**：中转的身份和截止日期回答应与官方一致。

### 已移除：Mojibake / 分词器怪癖检测
旧版本会根据日文和罗马音输出中的"Mojibake 模式"打分。但没有资料证明这种模式是 Claude 特有的，结果也无法复现，所以删除了这一项。现在改用基线 `input_tokens` 对比，它直接测量分词器。

## monitor.py

对 4 类探测（截止日期、身份、推理、风格）连续跑 N 轮，全部用流式请求，并报告：
- **同类探测内部**的 TTFT 和吞吐量异常值。用 IQR 方法，至少需要 5 个样本，而且与中位数相差至少 30% 才算异常。10% 以上样本出现"变快"的异常时，判为 high。
- 自称为非 Claude 模型的回答（critical）。
- 风格异常：长度异常或出现意外的中文（medium）。
- 与中位数相差超过 12 个月的截止日期回答（medium；24 个月以上为 high）。小幅波动是正常的。

失败的请求会作为错误列出，并从分析中排除。成功请求不到一半时判为 INCONCLUSIVE。其他判定依次为 MODEL MIXING DETECTED、SUSPICIOUS、MOSTLY CONSISTENT、CONSISTENT。

## 局限性

- 没有任何一项检测能 100% 准确，高级中转可以绕过所有独立检测。
- 中转可以人为加延迟、改写响应头和模型字段、注入系统提示词。
- 自报的截止日期和身份很容易被影响。
- 没有官方基线时，工具只能给出"未发现掺水"，不能证明"是真的"。
- 最佳做法：使用 `--official-key`，并在不同时段运行 `monitor.py`。

## 使用建议

1. **不同时段测试**：有些中转只在高峰期掺水。
2. **使用官方基线**：这是唯一难以伪造的检测。
3. **关注定价**：如果 Opus 大幅打折，要问问是怎么做到的。
4. **测试 Claude 独有功能**：比如 adaptive thinking、工具调用行为。
5. **持续监控**：中转商可能随时更换后端模型。
