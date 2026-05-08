# Claude 中转 API 模型掺水检测工具

检测第三方 Claude API 中转站是否偷偷将请求路由到更便宜的模型（DeepSeek、GPT-3.5、Qwen 或更小的 Claude 模型），而不是你付费购买的模型。

## 背景

Claude API 中转市场已经爆发——超过 100+ 家第三方服务声称提供 Claude 访问。调查显示，部分中转商会将昂贵模型（Opus）替换为更便宜的模型（Sonnet、Haiku，甚至 GPT-3.5），从中赚取差价。

常见的掺水手段：
- **模型降级**：你付 Opus 的钱，实际给你 Sonnet 或 Haiku
- **跨平台替换**：你付 Claude 的钱，实际给你带 Claude 系统提示词的 GPT-4-mini
- **分时段切换**：测试时给真 Claude，凌晨低峰期切换到便宜模型
- **按请求切换**：简单问题给真 Claude，复杂问题切到便宜模型省钱

## 工具说明

| 工具 | 用途 | 场景 |
|------|------|------|
| `detect.py` | 一次性 6 层验证 | 这个中转是不是真的？ |
| `monitor.py` | 连续 N 轮监控 | 这个中转有没有**间歇性掺水**？ |

## 工作原理

### detect.py — 6 层验证

| 层级 | 测试 | 检测目标 |
|------|------|---------|
| 1 | **魔术字符串** | 是否为官方渠道（渠道指纹） |
| 2 | **知识截止日期** | 通过时间锚点判断模型世代（最难伪造） |
| 3 | **延迟 & TPS** | 通过物理规律判断模型大小（无法伪造） |
| 4 | **身份 & 拒绝** | Claude 特有的行为模式 |
| 5 | **分词器签名** | 模型特有的编码怪癖（Mojibake） |
| 6 | **响应头 & 模型字段** | API 返回的元数据 |

### monitor.py — 连续监控

发送 N 轮相同请求，通过统计分析捕获间歇性掺水：
- **知识截止一致性**：不同的日期 = 不同的模型
- **身份泄漏**：DeepSeek/Qwen 意外暴露自身身份
- **语言切换**：中文意外泄漏（DeepSeek 默认中文回复）
- **延迟/TPS 异常值**：突然变快的响应 = 更便宜的模型

## 核心原理

**物理规律无法伪造。** 大模型（Opus，约 2T 参数）物理上不可能像小模型（Haiku）那样快速输出 token。如果你请求 Opus 但在 1 秒内收到响应、TPS 超过 85，那绝不是 Opus。

**记忆边界难以伪造。** 每个模型在预训练阶段都有特定的知识截止日期。系统提示词可以改变模型的"性格"，但无法完美伪造知识边界。不带系统提示词提问，迫使模型暴露真实的时间锚点。

**魔术字符串** 是 Anthropic 官方的一个未公开机制——特定哈希字符串会触发官方渠道的拒绝响应。转发到非 Anthropic 后端的中转站不会触发此行为。

## 安装

```bash
pip install httpx
```

## 使用方法

### detect.py — 一次性检测

```bash
# 基础检测（仅中转）
python detect.py \
  --proxy-url https://你的中转.com/v1 \
  --proxy-key sk-你的密钥 \
  --model claude-opus-4-6-20250514

# 带官方 API 对照
python detect.py \
  --proxy-url https://你的中转.com/v1 \
  --proxy-key sk-你的密钥 \
  --model claude-opus-4-6-20250514 \
  --official-key sk-ant-官方密钥
```

### monitor.py — 连续监控

```bash
# 快速检查（20 轮，约 2 分钟）
python monitor.py \
  --proxy-url https://你的中转.com/v1 \
  --proxy-key sk-你的密钥

# 深度检查（50 轮，间隔 5 秒）
python monitor.py \
  --proxy-url https://你的中转.com/v1 \
  --proxy-key sk-你的密钥 \
  --rounds 50 --interval 5

# 急速模式（无延迟）
python monitor.py \
  --proxy-url https://你的中转.com/v1 \
  --proxy-key sk-你的密钥 \
  --rounds 30 --interval 0
```

## 输出示例

### detect.py 输出

```
============================================================
  Score: 9/10 (90%)
  Verdict: LIKELY AUTHENTIC — probably real Claude
============================================================
```

| 分数 | 判定 | 含义 |
|------|------|------|
| 80-100% | LIKELY AUTHENTIC | 大概率是真 Claude |
| 50-79% | SUSPICIOUS | 可能有掺水或降级 |
| 0-49% | LIKELY SWAPPED | 大概率不是声称的模型 |

### monitor.py 输出

```
============================================================
  VERDICT: MODEL MIXING DETECTED — proxy is routing to different models
  Estimated mixing rate: ~30% of requests
============================================================
```

## 各模型的预期指标

### 知识截止日期

| 模型 | 预期截止 |
|------|---------|
| Claude Opus 4.6 | 2025-03 |
| Claude Sonnet 4.6 | 2025-02 |
| Claude Haiku 4.5 | 2025-03 |
| Claude Sonnet 4.5 | 2025-02 |
| Claude Opus 4.5 | 2025-02 |
| Claude Sonnet 4 | 2025-02 |

### 延迟与速度

| 模型 | 预期首 Token 时间 | 预期 TPS |
|------|-----------------|----------|
| Opus | 1.5-3.0s | 25-45 tokens/s |
| Sonnet 4.6 | 0.8-2.0s | 30-55 tokens/s |
| Haiku | 0.2-0.5s | 100-200 tokens/s |

Bedrock 实测 Sonnet 4.6 基线（10 轮）：
- 延迟：4.31s 平均（标准差 1.12s），输出约 155 tokens
- TPS：37.3 平均（范围 20-42）
- 截止日期："2025-02"（8/10 一致）

### 真实压测数据对比

来源：[cnblogs.com/sprinng](https://www.cnblogs.com/sprinng/p/19574478)

| 指标 | 官方 Opus | 官方 Sonnet | 某低价"Opus"（实际是 Sonnet） |
|------|----------|------------|----------------------------|
| 首字延迟 | ~1.5-2.5s | ~0.6-1.0s | 0.7s（太快了！） |
| 输出速度 | ~25-40 tps | ~70-100 tps | 85 tps（Sonnet 的速度） |
| 复杂推理 | 92/100 | 85/100 | 58/100 |
| 知识截止 | 2025-03 | 2025-03 | 2024-10（实锤） |

## 实测验证（Bedrock）

我们用 AWS Bedrock（官方一手渠道）验证了工具的准确性：

```
  Profile: global.anthropic.claude-sonnet-4-6
  Cutoff: 2025-02 (8/10 一致)
  Avg latency: 4.31s (stdev: 1.12s, ~155 tokens 输出)
  TPS: 37.3 tokens/s avg
  Identity: "I'm Claude, an AI assistant made by Anthropic" (5/5 一致)
  Refusal: 拒绝扮演 GPT-4、DeepSeek、Qwen
  Verdict: 无掺水，真实 Claude
```

## 使用建议

1. **不同时段测试** — 有些中转只在高峰期掺水
2. **测试复杂推理** — 简单问题看不出模型差异
3. **关注定价** — 如果 Opus 打 8 折，要质疑怎么做到的
4. **测试 Claude 独有功能** — extended thinking 等功能 GPT 无法模拟
5. **持续监控** — 每周跑一次，中转商可能随时换后端模型

## 局限性

- 单一测试无法 100% 准确
- 高级中转可能人为添加延迟模拟 Opus 速度
- 魔术字符串检测可能随 Anthropic 更新而变化
- 知识截止可以通过 RAG 部分伪造
- 最佳效果：组合所有测试 + 不同时间多次运行

