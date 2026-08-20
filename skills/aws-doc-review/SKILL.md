---
name: aws-doc-review
description: >-
  Fact-check AWS technical documents against official AWS documentation. Extracts atomic claims,
  verifies each against docs.aws.amazon.com, reports findings with severity and citations.
  Use when the user says "review document", "fact-check", "verify this doc", "prüfe", "check for errors".
  Verification only — never edits the document. AWS content only.
---

# AWS Doc Review

## Overview

对技术文档进行事实核查（fact-check），提取所有 AWS 相关声明，逐条验证其准确性，输出结构化审核报告。适用于 Quick Research 输出、客户交付物、内部 wiki 内容、PPT/Word 文档。目标是确保发给客户的材料中不含幻觉数据、虚构功能或过期信息。

**Scope: AWS only.** 权威来源始终是 AWS 官方材料 — `docs.aws.amazon.com` 优先，然后 `aws.amazon.com/blogs`、AWS What's New / release notes。社区内容（Stack Overflow、Medium、个人博客）永远不是权威来源。

**本 skill 只验证，不修改文档**，也不输出聚合质量分 — 19 条正确、1 条服务限制写错的文档不是"95% 好"，而是一份含阻塞性错误的文档。

## Parameters

- **input_path** (required): 文件路径或目录路径
- **prior_input** (optional): 上一轮 review 笔记 / 同事反馈，用于对比当前版本
- **source_policy** (optional, default `public-only`): `public-only` 仅引用公开 AWS 文档；`include-internal` 额外搜索内部源
- **output_path** (optional): 报告输出目录，默认与 input_path 同目录
- **email_draft** (optional, default `false`): 是否生成邮件草稿

## Core principle: fail loud

无法验证的声明是一条 **finding**，不是默认判定。当查询失败、工具缺失、页面 404 或来源矛盾时，必须标记 ⚪ Unverifiable 并说明原因，**不得**把不确定收敛成 🟢 或 🔴。

**Why:** 会静默猜测的 fact-checker 比没有更糟，因为读者会信任它。"我无法确认这一条"是有用的结果；编造的判定会让报告里其他每一行都失去可信度。

## Workflow

### Step 1: 加载文档

**Mode:** deterministic
**Tool:** file_read / file_read_pdf / file_read_docx / file_read_pptx
**Input:** `{{input_path}}`
**Output:** 文档全文内容
**Validate:** 内容非空且格式正确
**On failure:** 提示用户检查文件路径和格式

支持格式：`.md`、`.txt`、`.docx`、`.pdf`、`.html`、`.pptx`。

- `.docx` 用 `python3 -c "from docx import Document; ..."`；`.pdf` 用 `python3 -c "import pymupdf; ..."`；`.pptx` 用 `python3 -c "from pptx import Presentation; ..."`。缺库时必须 `pip install`，不得跳过文件
- 如果 input_path 是目录，自动发现目录中所有支持格式的文件
- 如果 input_path 是单个文件，读取完整内容
- 读取完整内容后，向用户展示文件列表并确认后再继续
- 单次审核不超过 10 个文档，超过建议分批处理（质量随数量增加而下降）
- 如果 `{{prior_input}}` 提供了路径，读取 prior review 内容，在 Step 4 中对比每条 prior finding 的当前状态：✅ Already addressed / ⚠️ Still present / 🔄 Partially addressed

### Step 2: 提取声明

**Mode:** agentic
**Input:** 文档全文
**Output:** 可验证声明列表（claim ledger）
**Validate:** 至少提取出 3 条可验证声明
**On failure:** 文档可能不包含 AWS 技术内容，通知用户

提取范围：AWS 服务能力/功能/限制、定价数据、区域可用性、架构模式、模型能力声明、EOL/废弃日期。忽略主观评价和无法验证的观点。

- 每条 claim 必须是 **atomic** — 只包含一个可独立验证的断言。复合声明必须拆分："Lambda 最长运行 15 分钟且每百万请求 $0.20" 是两条
- 原子性判据是**一次来源查询能否 settle 它**。需要查两个不同页面才能确认的，拆开；总是从同一页同一句话得出的，合并。不要为了 ledger 更长而拆 — ledger 是覆盖度的证据，不是数量指标
- 每条 claim 必须有稳定 ID（`C1`、`C2`…）和位置（章节标题或行号），便于回溯
- 必须检查每个提到的 AWS 服务、Bedrock 模型、Lambda runtime、API 版本的 EOL/废弃状态，即使文档没提生命周期 — 推荐一个已死的组件是严重缺陷。**通过的检查不产生 ledger 行**（否则 ledger 会被文档从未声称的内容淹没），把检查范围记在报告的 Coverage 行即可
- 但**一旦发现某组件已过期或临近 EOL，必须补一条 ledger 行**（例如 `C7 | 文档推荐使用 X（未标注 X 已于 YYYY-MM-DD 结束支持）| § 章节 | 🔴 EOL/Deprecated`），因为每条 finding 都必须对应一个 ledger 行，否则计数与 ledger 无法对齐。文档"推荐使用某组件"本身就隐含了"该组件当前可用"这一可验证声明
- "AWS 推荐 X" 这类归因给 AWS 的最佳实践声明**是可验证的** — 验证这个归因是否成立
- 非 AWS 技术的声明**超出范围**：在 ledger 中记为 ⚪ 并注明 "outside AWS scope — not checked"，不做研究，让读者知道它被看到且被有意跳过
- 不得修改原始文档

### Step 3: 验证声明

**Mode:** agentic
**Tool:** `aws_knowledge_mcp_server__aws_search_documentation`, `aws_knowledge_mcp_server__aws_read_documentation`, `aws_knowledge_mcp_server__aws_get_regional_availability`, web_search, url_fetch
**Input:** 声明列表 + `{{source_policy}}`
**Output:** 每条声明的验证结果和来源 URL
**Validate:** 每条声明都有对应的验证结果
**On failure:** 标记为 ⚪ Unverifiable 并注明原因

验证源优先级：

1. `aws_knowledge_mcp_server__aws_search_documentation` — 搜索 AWS 官方文档索引（首选，最精准）
2. `aws_knowledge_mcp_server__aws_read_documentation` — 读取指定文档 URL 转 markdown（用于深入验证具体页面）
3. `aws_knowledge_mcp_server__aws_get_regional_availability` — 验证服务/feature 的区域可用性（结构化数据）
4. `web_search` + `url_fetch` — 补充验证定价页、博客等（`site:aws.amazon.com/pricing`、`site:aws.amazon.com/blogs`）
5. 如果 `source_policy = "include-internal"`，搜索 Slack 相关频道获取额外上下文。如果 Slack 工具不可用，静默跳过并仅依赖公开源验证

**降级路径**：如果 AWS Knowledge MCP 未连接，降到 `web_search` + `url_fetch` 限定 `site:docs.aws.amazon.com`。如果 `web_search` 也不可用，可以构造 `docs.aws.amazon.com` URL 直接 fetch，**但必须确认抓到的页面真的写了这个事实** — 404 或页面不含该声明都不算验证。必须在报告 header 的 **Retrieval method** 行记录实际用到的层级，以及**哪一层是因为工具不可用而跳过的**（否则每份报告都显示最低层，低估了自身严格程度）。

**验证规则：**

- 每条声明必须找到具体来源 URL 和具体章节/表格。不能因为"听起来合理"就假设正确
- **证据缺失（evidence by absence）**：有些结论只能由"官方页面里没有它"推出 — 例如某模型已从 Bedrock 模型目录中移除，说明它已下线。这种推理**允许**，但必须满足三个条件：(1) 列出实际查过的页面 URL；(2) 该页面是**穷举性清单**（模型目录、支持区域表、runtime 列表），而不是任意一篇文档；(3) 在 finding 中明确标注这是由缺失推出的结论，不得写成引用原文。不满足则判 ⚪
- 定价、模型、区域可用性声明必须交叉验证 ≥2 个官方源（pricing page vs 文档 vs FAQ 可能不同步）。此规则适用于**值本身随区域/层级变化**的声明 — 区域限定文档中陈述的全局固定限制不算区域声明
- ≥2 源规则**只适用于确认一个值**，不适用于**否证一个全称断言**。"所有区域都支持 X" 只需一个反例即可判 🔴 — 一个官方页面列出有限区域清单就足够。不得因为凑不够两个源而把已经证伪的声明降级为 ⚪，那等于把真实错误埋在取证配额后面
- 硬限制和配额查一个官方页面即可，但**配额页面没有不等于限制不存在**。Quotas 页往往只覆盖可调整的吞吐类配额，固定结构性上限常在 constraints / limits / 开发者指南页。记 ⚪ 之前必须再查至少一个官方页面，否则会把确实存在的硬限制误报成"未记录"
- 两个**覆盖同一平台同一范围**的官方源矛盾时必须标 🔴 Contradictory 并给出两个 URL，不得静默选一个。不同平台对同一事物发布不同值**不是矛盾** — AWS 托管服务的 EOL 日期与模型提供方自己的日期本来就可以不同，某区域价格与 us-east-1 价格本来就不同。这类情况按文档声明的范围判 🟢，或在文档引错时判 🟡 Region-specific
- 超过 ~8 条声明时应当用 subagent 并行验证（每条查询互相独立）。但**不得**在没有来源 URL 的情况下直接采信 subagent 的结论
- `source_policy = "public-only"` 时不得使用机密或内部文档作为引用来源，因为审核报告可能会分享给客户
- 必须记录任何有意未查的声明（超出范围、抽样、截断）— 静默省略会被读成"全部覆盖了"

### Step 4: 分类发现

**Mode:** agentic
**Input:** 验证结果
**Output:** 分类后的发现列表
**Validate:** 每条发现有明确的级别和 Action；ledger 行数 == 各级别计数之和
**On failure:** 无法定级的标记为 ⚪ Unverifiable（**不得**默认降级为 🟡 — 默认值必须指向"未确认"，不能指向一个具体判定）

分类体系（每条声明只归入**一个**级别，使各级计数之和等于 ledger 行数）：

- 🔴 **Incorrect**：错误的数字/日期/百分比
- 🔴 **Fabricated**：功能/行为根本不存在
- 🔴 **Contradictory**：两个 AWS 官方源互相矛盾（同平台同范围）
- 🔴 **EOL/Deprecated**：已到 EOL 但文档未标注
- 🟡 **Imprecise**：技术上没错但有误导，或缺少影响决策的关键细节
- 🟡 **Wrong source**：声明正确但引用了非权威来源
- 🟡 **Region-specific**：用了美国定价/可用性但部署在非美国区域，或版本/层级不匹配
- ⚪ **Unverifiable**：没有权威来源能确认或否定。必须写明查了什么、返回了什么
- 🟢 **Correct**：已验证正确

- 每条 finding 标题必须前缀子类型，例如 `### 1. [Fabricated] GraphRAG 全区域可用`
- 每条 🔴 / 🟡 / ⚪ 必须附带 Action 建议和来源 URL
- 必须区分 Incorrect（数据错，find-and-replace 即可）和 Fabricated（功能不存在，需要删段并重新组织论述）
- ⚪ 的 Action 必须指出**谁或什么能定论** — 要读的配置文件路径、要问的团队或 AWS、或者"删掉这个具体数字保留定性表述"
- 技术上正确但有误导的声明只归 🟡，**不得**同时出现在 🟢 里，否则计数无法与 ledger 对齐
- 如果有 prior_input，对每条 prior finding 标注当前状态（✅/⚠️/🔄），放在报告 "Prior Input" section 中

### Step 5: 生成审核报告

**Mode:** deterministic
**Tool:** file_write
**Input:** 分类后的发现列表
**Output:** `{{output_path}}/review-<document-name>.md`（默认与 input_path 同目录）
**Validate:** 文件成功写入且包含所有 section
**On failure:** 在对话中直接输出报告内容

按 `references/review-report-template.md` 中的模板格式生成报告。文件名使用 kebab-case：`review-<document-name>.md`（对中文文档名使用拼音或英文翻译）。对目录审核使用 `review-<directory-name>.md`。

- 顺序：Prior Input → Claim Ledger → 🔴 → 🟡 → ⚪ → 🟢 → Recommendation
- 🔴 排在 🟡 之前。必须包含 "Verified Correct" 部分（只报失败的审核让读者无法判断覆盖度）
- **四个级别标题（🔴/🟡/⚪/🟢）即使为空也必须保留**，下面写 `_None._` — 缺失的标题和被遗漏的级别无法区分。此规则**只针对级别标题**；没有 prior_input 时 "Prior Input" 整节省略
- **Retrieval notes**：验证过程本身值得记录的曲折必须写在 header 的 Retrieval notes 里，即使最终判定是 🟢 或 🔴。例如"配额页没有该限制，在 constraints 页找到"、"该 EOL 结论由三个页面共同的沉默推出，非原文引用"。这类信息在 finding 正文里无处安放，但读者需要它来判断证据强度
- ledger 行数必须等于各级别计数之和，两者都要写在 Recommendation 里供读者核对
- 必须在 Recommendation 中包含客户中心性结构评估：检查文档是否先建立客户当前状态和目标再推解决方案，如果文档跳过客户背景直接介绍架构或功能，必须标注（"working backwards" 原则）。**仅对客户可见/对外分享的文档做此项**；内部笔记、草稿、参考资料跳过，因为对个人草稿做结构说教是噪音
- 写入文件后在对话中展示摘要（🔴/🟡/⚪/🟢 计数 + 文件路径）

### Step 6: Self-Review and Finalize

**Mode:** agentic
**Input:** 已生成的报告内容
**Output:** 修正后的最终报告
**Validate:** 5 个自检问题均通过
**On failure:** 修正不合格项后重新写入文件

写完报告后强制一轮自检，回答以下 5 个问题：

1. **Actionability** — 每个 🔴/🟡 的 Action 是否一次编辑就能改？"clarify this" 不算，得写成 "find-and-replace X → Y"、"删除第 N 行"、"在 X 后补充 Y"。不合格的必须重写。
2. **Source integrity** — 引用的每个 URL 是否这轮真正 fetch 过？搜索结果里瞄一眼见到的不算，得实际抓取过页面内容确认。未实抓的来源必须补抓或标注 "未验证原文"。
3. **Severity calibration** — 文档自己的免责声明（如"仅供参考"、"以官网为准"）该不该软化 finding？双向校准：既防止虚增（文档已声明近似值却被标 🔴），也防止偷懒下调（严重错误不能因免责声明就降级为 🟡）。
4. **Category coverage** — Step 2 的 8 类 claim（capabilities / features / limits / pricing / behavior / region / EOL / architecture）有没有漏一整类没查？如果文档包含某类声明但验证部分完全没覆盖，必须补查。
5. **Ledger arithmetic** — 用脚本核对，不要目测：ledger 行数是否等于 🔴+🟡+⚪+🟢 计数之和？每个 claim ID 是否只出现一次？不平必须修正。目测计数是这一步最常见的失效方式。

**自检不只用于加重判定。** 如果补查后发现某条 finding 被高估（原文其实支持该说法、或误读了页面），必须下调或删除。只会升级不会降级的自检是坏的自检。

自检结果不写入报告，但如果发现问题必须修正报告后重新写入文件。

### Step 7: 生成邮件草稿（可选）

**Mode:** agentic
**Input:** `{{email_draft}}` + 发现列表
**Output:** 邮件文本
**Validate:** 邮件包含所有 🔴 和 🟡 发现
**On failure:** 跳过此步骤

仅在 `email_draft = true` 或用户明确要求时执行。邮件只包含 🔴 / 🟡 / ⚪，不列举 🟢。语气建设性。**不自动发送**，草稿留在对话中供用户先审阅。

## Output

最终交付物：`review-[文档名].md` 文件，包含 Claim Ledger、Critical/Medium/Unverifiable 发现（含来源和修复建议）、已验证正确的声明、整体推荐。

## Methodology: THELMA-Inspired Verification

本 skill 的声明提取和验证流程借鉴了 Amazon 内部研究论文 THELMA（Task Based Holistic Evaluation of LLM Applications, arXiv:2505.11626）的 **Decompose → Match → Aggregate** 范式：

**Decompose（Step 2）：**
- 将文档拆解为 atomic claims：每条 claim 只包含一个可独立验证的事实断言
- 不允许复合声明（如 "A 支持 X 且价格为 Y" 必须拆成两条）
- 这确保了验证粒度足够细，不会因为一条声明"部分正确"而漏判

**Match（Step 3）：**
- 对每条 claim 做 binary grounding judgment：Grounded（有 authoritative source 支撑）或 Not Grounded（无支撑）
- 不允许"可能正确"的中间态。如果 source 不足以确认也不足以否定，标记为 ⚪ Unverifiable 而非默认正确
- 交叉验证多个 source（THELMA 的 "cross-reference" 原则）：定价/模型/区域类 claim 需在 ≥2 个 authoritative source 中找到明确支撑

**Aggregate（Step 4~5）：**
- 按 severity taxonomy 汇总，而非简单计数
- 区分 "wrong data"（Incorrect）和 "invented feature"（Fabricated），后者对客户信任损害更大
- 提供 Verified Correct 列表建立信任（THELMA 的 evidence transparency 理念）
- **不输出聚合分数** — THELMA 的分数用于衡量系统质量趋势，而文档审核需要的是定位。平均分会把那一条致命错误抹掉

**核心原则：** 不因"没有反证"就假设正确（THELMA 论文核心发现：plausible-sounding claims 是幻觉最危险的形态）。

## Examples

### 审核目录中所有文档

```
input_path: "/path/to/docs/"
source_policy: "public-only"
```

触发："帮我审核这个文件夹里所有文档的准确性"

### 审核单个文档并生成邮件

```
input_path: "/path/to/bedrock-overview.md"
email_draft: true
```

触发："review this document and draft an email with findings"

### 基于上一轮反馈审核

```
input_path: "/path/to/document.docx"
prior_input: "/path/to/colleague-feedback.md"
```

触发："审核这个文档，参考上次的反馈看哪些问题修好了"

## Lessons Learned

### Do
- 用 `site:` 限定搜索范围提高验证准确率
- 交叉验证定价数据（pricing page vs 文档 vs FAQ 可能不同步）
- 区分 "incorrect"（数据错）和 "fabricated"（功能不存在）
- 配额页找不到某个限制时，再查 constraints / 开发者指南页，不要直接判"未记录"

### Don't
- 不要只因为"没找到反证"就标记为 Correct
- 不要修改原始文档
- 不要在邮件中列举所有 Verified Correct 项
- 不要把"不确定"默认收敛成某个具体级别 — 默认值必须是 ⚪

### Common Failures
- 定价数据变动频繁，文档可能写的时候正确但现在过时
- 某些预览版功能文档不完整，难以验证
- 中国区域定价和可用性与全球不同
- AWS 与模型提供方发布的 EOL 日期不同，容易被误判成 Contradictory

## When to Ask the User
- 文档涉及非公开 roadmap 信息时
- 无法确定目标部署区域时
- 发现数量超过 20 条时，询问是否按优先级截断
