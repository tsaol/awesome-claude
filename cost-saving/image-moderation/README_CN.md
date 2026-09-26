# 图片内容审核流水线

**中文** | [English](README.md)

基于 Claude 视觉能力的低成本图片内容审核方案。结合图片预处理、感知哈希和分层模型级联。按 [`examples/cost_comparison.py`](examples/cost_comparison.py) 中的示例假设，实时流水线比"原始 4K 图片直接发给 Sonnet"便宜 **~91%**，批量模式便宜 **~96%**。实际数字取决于你的流量 —— 请用自己的参数重新运行脚本。

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
│  图片预处理  │ ← EXIF 方向校正、透明背景转白、缩放至 768px、JPEG 质量 75
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Claude Haiku │ ← Haiku 4.5：快速、便宜的初审
└──────┬───────┘
       │ 置信度低于阈值（无论判定结果），或无法解析/拒绝/出错
       ▼
┌───────────────┐
│ Claude Sonnet │ ← Sonnet 5：对不确定案例复审
└───────────────┘
       │ 仍无法判定
       ▼
  needs_review=True, safe=False（绝不默认放行）
```

## 降本策略概览

| # | 策略 | 节省幅度 | 实现方式 |
|---|------|---------|---------|
| 1 | 图片缩放 | 图片 token 减少 72–91% | 4K→768×432 ≈ 443 token，对比 1,568（Haiku）/ 4,784（Sonnet 5） |
| 2 | 分层级联 | 大部分请求停留在便宜模型 | Haiku 优先，仅低置信度结果升级 |
| 3 | 批量 API | 所有 token 5 折 | 非实时任务半价处理 |
| 4 | 结构化输出 | 输出 token 节省 ~80% | 纯 JSON 响应（~30 token）vs 冗长文本 |
| 5 | 预过滤（pHash） | 已知图片节省 100% | 已见过的违规图片零 API 成本 |
| 6 | 提示词缓存 | **内置提示词下无效果** | 提示词低于模型最小可缓存长度，见下文 |

### 成本明细（100 万张/月，来自 `examples/cost_comparison.py`）

价格：Haiku 4.5 输入/输出 $1 / $5，Sonnet 5 $2 / $10（每百万 token）。流量参数（4K 16:9 上传、~320 提示词 token、冗长输出 150 vs JSON 输出 30 token、10% 升级率、5% pHash 命中率）均为**假设输入**，并非实测数据。

| # | 步骤 | 每张 token | 月成本 | 对比基准 |
|---|------|-----------|-------|---------|
| 1 | 基准：原始 4K → Sonnet 5，冗长输出 | 输入 5,104 / 输出 150 | $11,708 | — |
| 2 | 缩放至 768px → Sonnet 5 | 输入 763 / 输出 150 | $3,026 | -74.2% |
| 3 | 缩放 → Haiku 4.5，纯 JSON 输出 | 输入 763 / 输出 30 | $913 | -92.2% |
| 4 | 提示词缓存 | — | 节省 $0 | — |
| 5 | 级联：Haiku + 10% 升级到 Sonnet | | $1,096 | -90.6% |
| 6 | + pHash 预过滤（5% 免费） | | **$1,041** | **-91.1%** |
| 7 | 批量 API，仅 Haiku（非实时） | | **$434** | **-96.3%** |

第 5 步比第 3 步贵，因为升级是为不确定图片多付一次复审费用 —— 这是为准确率花钱，不是省钱。批量模式只运行单个模型，没有升级。

---

### 策略 1：图片缩放

**原理：** Claude 将图片按输入 token 计费，约为 `宽 × 高 / 750`。超过模型上限的图片会先由 API 自动缩小：Haiku 4.5 长边缩到 1,568 px（单张上限约 1,568 token），Sonnet 5 长边缩到 2,576 px（最多约 4,784 token）。所以原始 4K 图片并不是"8,000 token" —— 在 Haiku 上约 1,568，在 Sonnet 5 上约 4,784。自己先缩放到 768 px 可降到几百 token，并减小上传体积。768 px 通常足以识别违规内容，但请用自己的数据验证。

**不同分辨率的 token 数**（`estimate_image_tokens`）：

| 分辨率 | Haiku 4.5 | Sonnet 5 |
|-------|-----------|----------|
| 200×200 | ~54 | ~54 |
| 400×400 | ~214 | ~214 |
| 768×432 | ~443 | ~443 |
| 768×768 | ~787 | ~787 |
| 1080×1920 | ~1,568（已缩小） | ~2,765（已缩小） |
| 3840×2160（4K） | ~1,568（已缩小） | ~4,784（已缩小） |

**实现：** `preprocess_image` 会应用 EXIF 方向、将透明图片（RGBA/LA/P）合成到白色背景、缩放至 `max_size=768`，并重新编码为 JPEG 质量 75（同时去除 EXIF 元数据）。

```python
from image_moderation import preprocess_image

b64, meta = preprocess_image("photo_4k.jpg", max_size=768, quality=75)
print(meta)
# {'original_size': (3840, 2160), 'final_size': (768, 432), ...,
#  'estimated_tokens': 443, 'estimated_tokens_original': 1568}
```

---

### 策略 2：分层级联

**原理：** 大多数图片很容易判断，由便宜模型处理；只有不确定的才交给更强的模型。

| 级联层级 | 每张成本（示例） | 用途 |
|---------|---------------|------|
| pHash 预过滤 | $0 | 通过哈希匹配已知违规 |
| Claude Haiku 4.5 | ~$0.0009 | 其余所有图片的初审 |
| Claude Sonnet 5 | ~$0.0018（另加已付的 Haiku 调用） | 不确定案例的复审 |

**升级逻辑：** 如果 Haiku 的置信度低于 `sonnet_threshold`（默认 0.7）—— 无论判定为安全还是不安全 —— 或者回复无法使用（无法解析、拒绝、API 错误），图片会升级到 Sonnet。如果所有层级都无法判定，结果为 `needs_review=True` 且 `safe=False`，并计入 `stats["needs_review"]`。流水线绝不会把未审核的图片报告为安全。

```python
pipeline = ImageModerationPipeline(
    sonnet_threshold=0.7,
    cascade_levels=["phash", "haiku", "sonnet"],
)

print(pipeline.stats)
# {'total': 10000, 'resolved_at': {'phash': 500, 'haiku': 8600, 'sonnet': 900, ...},
#  'escalated': 900, 'needs_review': 12, 'total_cost': ..., ...}
```

`total_cost` 包含升级图片的 Haiku 调用费用。

---

### 策略 3：批量 API（成本降低 50%）

**原理：** Message Batches API 以异步处理（24 小时内返回）换取所有 token（输入、输出、缓存读写）5 折计费。适合夜间巡检、存量审核、策略更新后重审；不适合实时上传审核。

批量模式只用一个模型（启用 Haiku 时用 Haiku，否则用 Sonnet），没有升级。每张提交的图片都有结果：失败或过期的请求返回 `needs_review` 结果。每个结果带有 `details["custom_id"]`（按提交顺序为 `img_<序号>`）。

```python
import time
from pathlib import Path

images = sorted(Path("uploads/today/").glob("*.jpg"))
batch_id = pipeline.moderate_batch_async(images)

while pipeline.get_batch_status(batch_id) != "ended":
    time.sleep(60)

results = pipeline.get_batch_results(batch_id)
flagged = [r for r in results if not r.safe]   # 包含 needs_review
```

---

### 策略 4：结构化输出（输出 token 节省 ~80%）

两个模型的输出 token 价格都是输入的 5 倍（Haiku 4.5：$1 / $5，Sonnet 5：$2 / $10 每百万 token）。冗长解释通常需要 100–200 个输出 token，JSON 判定只需 ~30 个。系统提示词要求只输出 JSON，`max_tokens=100` 防止失控输出。在 Sonnet 5 上，此短分类任务显式关闭了 thinking。

回复解析是防御式的：去除代码块标记，未知类别映射为 `other`，置信度限制在 [0, 1]，任何不是"带布尔 `safe` 字段的 JSON 对象"的回复都变为 `needs_review` 结果。

---

### 策略 5：感知哈希预过滤（已知图片节省 100%）

感知哈希（pHash）为图片视觉内容生成指纹，对缩放、重新编码和小幅编辑都很稳健。已知违规图片的再次上传可以免费匹配。

`threshold` 参数（默认 8，64 位中的汉明距离）控制严格程度。哈希 CSV 中格式错误的行会被跳过并发出警告。

```python
from image_moderation.prefilter import PHashFilter
from image_moderation.models import ModerationCategory

phash = PHashFilter()
phash.add_hash(phash.compute_hash("known_spam_1.jpg"), ModerationCategory.SPAM)
phash.save_db("known_violations.csv")   # 每行 hash,category

result = phash.check("user_upload.jpg", threshold=8)
if result:
    print(f"匹配已知违规: {result.category}（置信度: {result.confidence}）")
```

---

### 策略 6：提示词缓存（对内置提示词无效）

客户端会给系统提示词加上 `cache_control`，但 API 只缓存达到模型最小长度的前缀：**Haiku 4.5 为 4,096 token**，**Sonnet 5 为 1,024 token**。内置提示词约 300 token，因此不会被缓存，`cached_tokens` 始终为 0。该标记无害。图片本身每次请求都不同，永远无法缓存。

如果你把提示词换成超过最小长度的长策略文档，缓存读取按输入价格的 0.1 倍计费，缓存写入按 1.25 倍计费。可通过 `result.cached_tokens`（`cache_read_input_tokens`）确认是否命中。

## 快速开始

需要 Python 3.9+。

```bash
cd cost-saving/image-moderation
pip install -e '.[dev]'
pytest -q        # 单元测试，不调用 API
```

### 单张图片

```python
from image_moderation import ImageModerationPipeline

pipeline = ImageModerationPipeline(max_image_size=768, sonnet_threshold=0.7)

result = pipeline.moderate("photo.jpg")
print(result.safe, result.needs_review)   # True/False；True 表示需要人工复核
print(result.category)                    # ModerationCategory.SAFE
print(result.cost_summary)
# Level: haiku | Tokens: 770in/28out (0 cache read, 0 cache write) | Cost: $0.000910
```

### 启用 pHash 预过滤

```python
pipeline = ImageModerationPipeline(
    hash_db_path="known_violations.csv",
    cascade_levels=["phash", "haiku", "sonnet"],   # "prefilter" 可作为 "phash" 的别名
)
```

## 配置参数

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `max_image_size` | 768 | 缩放最大尺寸（越小越便宜） |
| `image_quality` | 75 | JPEG 压缩质量 |
| `sonnet_threshold` | 0.7 | Haiku 置信度低于此值（无论判定结果）时升级到 Sonnet |
| `enable_cache` | True | 给系统提示词加 `cache_control`（仅当提示词超过模型最小长度时生效） |
| `cascade_levels` | 全部 | `phash`（别名 `prefilter`）、`haiku`、`sonnet` 的任意组合；未知名称抛出 `ValueError` |
| `client` | None | 预先构建的 `anthropic.Anthropic` 兼容客户端（便于测试） |

## 成本估算

```bash
python examples/cost_comparison.py
```

修改脚本顶部的假设参数（图片尺寸、升级率、pHash 命中率、输出长度）以匹配你的流量。默认参数下：

| 策略 | 月成本（100 万张） |
|------|-------------|
| 基准（原始 4K → Sonnet 5） | ~$11,700 |
| 缩放 → Haiku 4.5 | ~$913 |
| 完整实时流水线 | ~$1,041 |
| 批量，仅 Haiku | ~$434 |

## 项目结构

```
image_moderation/
├── __init__.py          # 公共 API
├── models.py            # 数据模型、枚举、定价、成本估算
├── preprocessing.py     # 图片方向/透明/缩放/编码 + token 估算
├── prefilter.py         # pHash 匹配已知违规
├── client.py            # Claude API 封装（解析、错误处理、批量）
└── pipeline.py          # 分层级联编排
examples/
├── basic_moderation.py  # 单张图片示例
├── batch_moderation.py  # 批量 API 示例（轮询直到 ended）
└── cost_comparison.py   # 成本计算器（假设参数）
tests/                   # 使用假 Anthropic 客户端的 pytest 测试
```
