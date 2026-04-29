# 图片内容审核流水线

**English** | [English Version](README.md)

基于 Claude 视觉能力的低成本图片内容审核方案。通过图片预处理、感知哈希和分层模型级联，实现 **95%+** 的成本降低。

## 架构

```
用户上传图片
    │
    ▼
┌──────────────┐
│  pHash 匹配  │ ← 已知违规图片哈希库（零 API 成本）
└──────┬───────┘
       │ 未命中
       ▼
┌──────────────┐
│  图片预处理  │ ← 缩放至 768px，JPEG 质量 75（减少 ~85% token）
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Claude Haiku │ ← 快速、便宜 — 处理 ~90% 的图片
└──────┬───────┘
       │ 置信度低
       ▼
┌───────────────┐
│ Claude Sonnet │ ← 仅处理模糊案例（~5-10%）
└───────────────┘
```

## 降本策略概览

| # | 策略 | 节省幅度 | 实现方式 |
|---|------|---------|---------|
| 1 | 图片缩放 | ~85% token 减少 | 4K→768px，token 从 ~8000 降至 ~1000 |
| 2 | 提示词缓存 | 系统提示词节省 ~90% | 跨请求缓存审核规则 |
| 3 | 分层级联 | ~90% 请求节省 | 大部分图片由 Haiku 或预过滤解决 |
| 4 | 批量 API | 每请求节省 50% | 非实时任务半价处理 |
| 5 | 结构化输出 | 输出 token 节省 ~80% | JSON 响应 vs 冗长文本 |
| 6 | 预过滤（pHash） | 已知图片节省 100% | 已见过的违规图片零 API 成本 |

**组合使用：总成本降低 ~95%+**

### 详细成本对照表（基准：100 万张/月，原始 4K → Sonnet）

| # | 策略 | 优化前 | 优化后 | 节省幅度 | 月成本影响 |
|---|------|-------|-------|---------|-----------|
| 1 | **图片缩放**（4K→768px） | ~8,000 输入 token/张 | ~1,000 输入 token/张 | **减少 85% 输入 token** | $18,000 → $2,250（-$15,750） |
| 2 | **提示词缓存**（系统提示词） | 500 token @ $3.00/M（Sonnet） | 500 token @ $0.30/M（缓存命中） | **系统提示词便宜 90%** | $1,500 → $150（-$1,350） |
| 3 | **分层级联**（Haiku 优先） | 100 万张 × Sonnet（$3.00/M 输入） | 90 万 × Haiku（$0.80/M）+ 10 万 × Sonnet（$3.00/M） | **平均每请求便宜 ~70%** | $3,000 → $1,020（-$1,980） |
| 4 | **批量 API**（异步 5 折） | 标准 API 定价 | 所有 token 5 折 | **整体账单 5 折** | $1,020 → $510（-$510） |
| 5 | **结构化输出**（纯 JSON） | ~150 输出 token @ $15.00/M（Sonnet） | ~20 输出 token @ $4.00/M（Haiku） | **输出成本降低 96%** | $2,250 → $80（-$2,170） |
| 6 | **pHash 预过滤**（已知图片） | 100% 图片调用 API | ~90% 图片调用 API（10% 免费过滤） | **减少 10% API 调用** | 在流水线层面节省 ~$50-100 |

> **注意：** 各行并非简单相加 — 策略之间是复合叠加关系。上表展示的是每个技术的独立影响。顺序组合后，总成本从 **~$18,000 降至 ~$33/月**。

### 逐策略成本瀑布图

```
$18,000  ← 基准：原始 4K 图片 → Sonnet，冗长输出
   │
   │  [1] 图片缩放（4K → 768px）             -85% 输入 token
   ▼
 $2,700
   │
   │  [2] 切换 Haiku + 提示词缓存            -73% 模型成本 + 缓存系统提示词
   ▼
   $730
   │
   │  [3] 分层级联（仅 10% → Sonnet）         -90% Sonnet 使用量
   ▼
   $340
   │
   │  [5] 结构化输出（150→20 token）          -87% 输出 token
   ▼
   $130
   │
   │  [6] pHash 预过滤（10% 零成本）          -10% API 调用
   ▼
   $117
   │
   │  [4] 批量 API（剩余部分 5 折）           -50% 所有 token
   ▼
    $58  ← 最终：完整流水线 + 批量处理
```

---

### 策略 1：图片缩放（减少 ~85% token）

**原理：** Claude 的视觉 API 根据像素数量将图片转换为 token。一张 4K 图片（3840×2160）消耗 ~8,000 个 token，而缩放到 768×768 后仅需 ~1,000 个 token。对于内容审核来说，低分辨率完全够用 — 违规内容（暴力、色情、仇恨符号）在低分辨率下同样一目了然。

**省钱机制：** 图片 token 按输入 token 计费。每张图从 ~8,000 降到 ~1,000 token，直接砍掉 85% 的单图输入成本。按 100 万张/月计算，仅此一项就能节省数千美元。

**不同分辨率的 token 消耗：**

| 分辨率 | 像素数 | 预估 Token 数 |
|--------|-------|-------------|
| 200×200 | 4 万 | ~170 |
| 400×400 | 16 万 | ~680 |
| 768×768 | 59 万 | ~1,000 |
| 1080×1920 | 200 万 | ~2,700 |
| 3840×2160（4K） | 830 万 | ~8,000+ |

**实现方式：** 缩放至 `max_size=768`，JPEG 压缩质量 75，同时去除 EXIF 元数据并将 RGBA 转为 RGB。

```python
from image_moderation import preprocess_image

b64, meta = preprocess_image("photo_4k.jpg", max_size=768, quality=75)
print(meta)
# {'original_size': (3840, 2160), 'final_size': (768, 432),
#  'bytes_original': 4200000, 'bytes_compressed': 85000,
#  'estimated_tokens': 1000}
```

---

### 策略 2：提示词缓存（系统提示词节省 ~90%）

**原理：** 每次审核请求都会发送相同的系统提示词 — 审核规则、分类定义和输出格式说明。不开缓存的话，每次请求都要为这些 token 付全价。Anthropic 的提示词缓存将系统提示词存储在服务端并跨请求复用，缓存命中时仅收取正常输入 token 费率的 10%。

**省钱机制：** 典型审核系统提示词为 500-1,000 个 token。100 万次请求/月，仅系统提示词就是 5 亿到 10 亿 token。按 Haiku 输入价格（$0.80/百万 token）计算，这就是 $400-800/月。开启缓存后，缓存命中价格为 $0.08/百万 token — 降至 $40-80/月。

**缓存命中率：** 在流量稳定的生产环境审核流水线中，缓存命中率通常超过 95%，因为系统提示词几乎不变。

```python
# 流水线默认启用缓存。
# 系统提示词设置 cache_control: {"type": "ephemeral"}
# 告诉 Anthropic 缓存约 5 分钟。
# 流量稳定时，几乎每个请求都命中缓存。

pipeline = ImageModerationPipeline(enable_cache=True)  # 默认值

# 在结果中查看缓存表现：
result = pipeline.moderate("image.jpg")
print(f"缓存 token 数: {result.cached_tokens}")  # 例如 1500 个输入 token 中有 500 个命中缓存
```

---

### 策略 3：分层级联（通过路由降低 ~90% 成本）

**原理：** 不是所有图片都需要同等级别的分析。大部分图片要么明显安全、要么明显违规 — 只有少部分真正模糊不清。对简单案例使用更便宜的模型（甚至不用模型），只对难判断的案例升级到贵模型，就能大幅降低平均单图成本。

**省钱机制：**

| 级联层级 | 单图成本 | 流量占比 | 用途 |
|---------|---------|---------|------|
| pHash 预过滤 | $0 | ~5-10% | 哈希匹配已知违规图片 |
| Claude Haiku | ~$0.001 | ~85-90% | 快速、便宜 — 处理大部分案例 |
| Claude Sonnet | ~$0.005 | ~5-10% | 高精度处理模糊内容 |

如果 90% 的图片由 Haiku 以 $0.001 处理，只有 10% 升级到 Sonnet 以 $0.005 处理，混合平均成本为 $0.0014/张，而非全部用 Sonnet 的 $0.005/张 — 仅 Claude API 成本就节省 72%。

**升级逻辑：** 当 Haiku 返回的结果置信度低于 `sonnet_threshold`（默认 0.7）时，图片自动升级到 Sonnet 进行二次判断。高置信度的安全图片永远不会升级。

```python
pipeline = ImageModerationPipeline(
    sonnet_threshold=0.7,  # Haiku 置信度 < 70% 时升级
    cascade_levels=["phash", "haiku", "sonnet"],
)

# 处理后查看图片在哪一层被解决：
print(pipeline.stats)
# {'total': 10000, 'resolved_at': {'phash': 500, 'haiku': 8600, 'sonnet': 900}, ...}
```

---

### 策略 4：批量 API（降低 50% 成本）

**原理：** Anthropic 的 Message Batches API 以异步处理换取所有 token 成本 5 折优惠。提交批量任务后在 24 小时内返回结果，而非实时响应。对于不需要即时结果的审核场景 — 如每晚回顾用户上传内容、历史内容审查或定期巡检 — 这相当于白送的优惠。

**省钱机制：** 5 折优惠适用于所有 token（输入、输出和缓存）。且与其他所有优化策略叠加。如果优化后的单图成本是 $0.001，批量 API 可以进一步降到 $0.0005。

**适用场景：**
- 每晚/每周的内容回顾巡检
- 历史存量内容审核
- 策略更新后的重新审核
- 训练数据标注

**不适用场景：**
- 实时上传审核（用户期望即时反馈）
- 直播内容过滤

```python
from pathlib import Path

images = list(Path("uploads/today/").glob("*.jpg"))
batch_id = pipeline.moderate_batch_async(images)  # 立即返回
print(f"已提交 {len(images)} 张图片，批次 ID: {batch_id}")

# 数小时后获取结果：
results = pipeline.get_batch_results(batch_id)
flagged = [r for r in results if not r.safe]
print(f"标记违规: {len(flagged)}/{len(results)}")
```

---

### 策略 5：结构化输出（输出 token 节省 ~80%）

**原理：** 在所有 Claude 模型中，输出 token 都比输入 token 贵得多：

| 模型 | 输入价格 | 输出价格 | 输出/输入比 |
|------|---------|---------|-----------|
| Haiku | $0.80/M | $4.00/M | **5 倍** |
| Sonnet | $3.00/M | $15.00/M | **5 倍** |

一个冗长的审核回复（"这张图片似乎包含了描绘暴力场景的内容..."）轻松消耗 100-200 个输出 token。而结构化 JSON 响应（`{"safe": false, "category": "violence", "confidence": 0.95}`）只需 ~20 个 token — 减少 80-90%。

**省钱机制：** 对于 100 万张图片使用 Haiku，将输出从 150 降到 20 个 token：
- 优化前：1.5 亿输出 token × $4.00/M = $600/月
- 优化后：2000 万输出 token × $4.00/M = $80/月
- **仅输出压缩就节省 $520/月**

**实现方式：** 系统提示词明确要求 Claude 只返回 JSON，`max_tokens` 设为 100（安全余量 — 实际响应约 20 个 token）。

```python
# 客户端强制结构化输出：
# - 系统提示词："Respond with ONLY a JSON object, no other text"
# - max_tokens=100（防止过长响应）
# - 响应格式：{"safe": bool, "category": str, "confidence": float, "reason": str}
```

---

### 策略 6：感知哈希预过滤（已知图片节省 100%）

**原理：** 感知哈希（pHash）根据图片的视觉内容生成指纹，对缩放、压缩和轻微编辑具有鲁棒性。通过维护一个已确认违规图片的哈希数据库，可以即时匹配重复上传和近似副本，完全不需要调用 Claude API。

**省钱机制：** 每张被 pHash 匹配的图片 API 调用成本为 $0。在用户重复上传相同违规内容的平台上（垃圾信息/滥用场景中很常见），这可以免费过滤掉 5-20% 的图片。

**如何处理变体：** 与精确文件哈希（MD5/SHA）不同，pHash 比较的是视觉相似度。两张图片即使：
- 不同文件格式（JPEG vs PNG）→ 相同 pHash
- 不同分辨率 → 相同 pHash
- 轻微裁剪或调色 → 相似 pHash（在阈值范围内）

`threshold` 参数（默认 8）控制匹配严格程度。越低 = 越严格，误报越少。越高 = 越宽松，能匹配更多变体但误报风险增加。

```python
from image_moderation.prefilter import PHashFilter
from image_moderation.models import ModerationCategory

# 从已确认的违规图片构建哈希数据库
phash = PHashFilter()
phash.add_hash(phash.compute_hash("known_spam_1.jpg"), ModerationCategory.SPAM)
phash.add_hash(phash.compute_hash("known_violence_1.jpg"), ModerationCategory.VIOLENCE)
phash.save_db("known_violations.csv")

# 生产环境中，匹配是即时且免费的：
result = phash.check("user_upload.jpg", threshold=8)
if result:
    print(f"命中已知违规: {result.category}（置信度: {result.confidence}）")
```

## 快速开始

```bash
cd cost-saving/image-moderation
pip install -e .
```

### 单张图片审核

```python
from image_moderation import ImageModerationPipeline

pipeline = ImageModerationPipeline(
    enable_cache=True,
    max_image_size=768,
    sonnet_threshold=0.7,
)

result = pipeline.moderate("photo.jpg")
print(result.safe)          # True/False
print(result.category)      # ModerationCategory.SAFE
print(result.cost_summary)  # Level: haiku | Tokens: 1050in/25out (500 cached) | Cost: $0.000640
```

### 批量处理（便宜 50%）

```python
from pathlib import Path

images = list(Path("uploads/").glob("*.jpg"))
batch_id = pipeline.moderate_batch_async(images)

# 稍后轮询（批量 API 在 24 小时内返回）
results = pipeline.get_batch_results(batch_id)
flagged = [r for r in results if not r.safe]
```

### 使用 pHash 预过滤

```python
pipeline = ImageModerationPipeline(
    hash_db_path="known_violations.csv",  # 每行格式：hash,category
    cascade_levels=["phash", "haiku", "sonnet"],
)

# 随时间积累哈希数据库
from image_moderation.prefilter import PHashFilter
phash = PHashFilter()
h = phash.compute_hash("confirmed_violation.jpg")
phash.add_hash(h, ModerationCategory.VIOLENCE)
phash.save_db("known_violations.csv")
```

## 配置参数

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `max_image_size` | 768 | 缩放最大尺寸（越小越便宜） |
| `image_quality` | 75 | JPEG 压缩质量 |
| `sonnet_threshold` | 0.7 | 低于此置信度触发 Sonnet 升级 |
| `enable_cache` | True | 缓存系统提示词，节省 90% token |
| `cascade_levels` | 全部 | 启用的层级：`phash`、`haiku`、`sonnet` |

## 成本估算

运行成本对比脚本：

```bash
python examples/cost_comparison.py
```

**100 万张图片/月** 的示例输出：

| 策略 | 月成本 |
|------|-------|
| 朴素方案（原图 → Sonnet） | ~$18,000 |
| 缩图 → Haiku | ~$1,000 |
| 完整流水线 + 批量 | ~$50 |

## 项目结构

```
image_moderation/
├── __init__.py          # 公共 API
├── models.py            # 数据模型、枚举、成本估算
├── preprocessing.py     # 图片缩放/压缩/编码
├── prefilter.py         # 感知哈希匹配已知违规图片
├── client.py            # Claude API 封装（缓存 + 批量）
└── pipeline.py          # 分层级联调度器
examples/
├── basic_moderation.py  # 单图审核示例
├── batch_moderation.py  # 批量 API 示例
└── cost_comparison.py   # 成本节省计算器
```
