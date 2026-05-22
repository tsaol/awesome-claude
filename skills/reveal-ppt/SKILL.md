---
inclusion: manual
---

# Reveal.js PPT Skill — 基于 reveal.js 的演示

> 调用方式：在聊天里输入 `#reveal-ppt` + 内容主题，我会用 reveal.js 框架生成一个带 Amazon brand 主题的 deck。
>
> 参考样本：`GlobalOperation/growth/framework-comparison/reveal-demo/index.html`

---

## 这个 skill 的定位

reveal.js 是最成熟的 HTML 演示框架。**单 HTML 文件 + 来自 jsdelivr CDN 的 reveal.js 引擎**。

**和 `#html-ppt` 的区别**：

| 维度 | `#html-ppt`（手搓） | `#reveal-ppt`（reveal.js） |
|------|---------------------|---------------------------|
| 依赖 | 完全零依赖 | 联网拉 CDN（首次约 100KB） |
| 翻页 | 我自己实现 | reveal.js 处理 |
| 过场动画 | 无 | slide / fade / zoom 多种 |
| 多列嵌套 slide | 不支持 | 支持（vertical sub-slides） |
| Speaker notes | 自己做的双栏 | reveal.js 内置 presenter mode（按 S 弹独立窗口） |
| 代码高亮 | 手写 | 内置 highlight.js |
| PDF 导出 | 浏览器打印 | `?print-pdf` 内置模式 |
| 适合场景 | 客户场地、离线、一次性 | 半正式演讲、tech talk、需要导出 PDF |

**优先用 `#html-ppt` 当默认**。只在以下情况选 `#reveal-ppt`：
- 需要 fancier 过场效果
- 需要 vertical sub-slides 做多层结构
- 需要 PDF 导出做存档
- 听众预期看到"专业演讲"风格

---

## 你的任务

当用户调用 `#reveal-ppt` 时：

### Step 1: 确认 4 件事

1. **主题 / 内容大纲**
2. **页数**（默认 8–12 页）
3. **是否要嵌入代码片段**（决定要不要加 highlight 插件）
4. **是否要 PDF 导出**（决定是否在 README 里写导出指令）

### Step 2: 生成一个单 HTML 文件

文件结构：

```html
<!DOCTYPE html>
<head>
  <link rel="stylesheet" href="...reveal.css">
  <link rel="stylesheet" href="...theme/black.css">  <!-- base theme，会被自定义 CSS 覆盖 -->
  <style>__AMAZON_BRAND_OVERRIDES__</style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <section>...</section>     <!-- 每个 section 是一张 slide -->
      <section>
        <section>...</section>   <!-- 嵌套 = vertical sub-slide -->
        <section>...</section>
      </section>
    </div>
  </div>
  <script src="...reveal.js"></script>
  <script src="...notes.js"></script>
  <script>Reveal.initialize({ ... });</script>
</body>
```

### Step 3: 套用 Amazon brand 主题（强制）

跟 `#html-ppt` 完全相同的色板和字体规则：

- 橙 `#FF9900` / 深橙 `#c45500`
- 深蓝 `#232F3E` / 浅橙 `#FFF8EE` / 边线 `#FFE0B2`
- 字体：`-apple-system, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif`
- 顶部 6px 渐变条（也可以用 reveal 的 progress bar）

### Step 4: reveal.js 特有元素（按需用）

**Speaker notes**：
```html
<section>
  <h2>...</h2>
  <aside class="notes">
    这页要怎么讲。注意停顿点。可能的问题。
  </aside>
</section>
```
按 `S` 打开 presenter mode（弹独立窗口，左主屏 / 右下张 + notes / 右上计时器）。

**Vertical sub-slides**（同一主题下钻）：
```html
<section>
  <section><h2>主题</h2></section>
  <section><p>子点 1</p></section>
  <section><p>子点 2</p></section>
</section>
```
按 ↓ 进入子页，→ 跳到下一个主题。

**Fragment（点击逐条出现）**：
```html
<ul>
  <li class="fragment">第一条</li>
  <li class="fragment">第二条</li>
</ul>
```

**自动列表（不按 fragment）**：直接 `<ul><li>...</li></ul>`

**代码块**（如果用户需要）：
```html
<pre><code class="hljs python" data-trim>
def hello():
    print("world")
</code></pre>
```

### Step 5: 标准 init 配置

```javascript
Reveal.initialize({
  hash: true,               // URL 带页号，可分享某一页
  controls: true,           // 右下小箭头
  progress: true,           // 底部进度条
  center: true,             // 内容垂直居中
  transition: 'slide',      // slide / fade / zoom / none
  slideNumber: 'c/t',       // 显示 "1/12"
  plugins: [ RevealNotes ]  // speaker notes
});
```

如果用户要代码高亮，加：
```javascript
plugins: [ RevealNotes, RevealHighlight ]
```
和对应 CDN：
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/monokai.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/highlight.js"></script>
```

### Step 6: 输出

直接生成完整 `<topic>-reveal.html`，给 `open` 命令，再列出常用快捷键：

- `← → ↑ ↓` 翻页
- `S` 打开 presenter mode（speaker notes 窗口）
- `F` 全屏
- `O` overview 概览
- `B` 黑屏
- `?` 看所有快捷键

如果需要 PDF 导出，在路径后加 `?print-pdf` 然后用浏览器打印。例：
```
open '<topic>-reveal.html?print-pdf'
# 然后 Cmd+P → Save as PDF
```

---

## 通用脚手架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>__TITLE__</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/black.css" id="theme">
  <style>
    /* === Amazon brand overrides === */
    :root {
      --r-main-color: #1a1a1a;
      --r-heading-color: #232F3E;
      --r-link-color: #FF9900;
      --r-background-color: #fff;
    }
    .reveal { font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif; color: #1a1a1a; }
    .reveal section { background: #fff; }
    .reveal h1, .reveal h2 { color: #232F3E; text-transform: none; }
    .reveal .accent { color: #FF9900; }

    /* Cover slide */
    .cover { background: linear-gradient(135deg, #232F3E 0%, #0d1421 100%) !important; }
    .cover h1 { color: #fff !important; }
    .cover .subtitle { color: #ccc; font-size: 0.6em; margin-top: 20px; }
    .cover .meta { color: #888; font-size: 0.4em; border-top: 1px solid #333; padding-top: 16px; margin-top: 30px; }

    /* Layouts (跟 #html-ppt 共用) */
    .layers { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 30px; }
    .layer { background: #FFF8EE; border: 2px solid #FFE0B2; border-radius: 12px; padding: 24px; }
    .layer .ln { font-size: 14px; color: #c45500; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; }
    .layer h4 { color: #232F3E; font-size: 22px; margin-bottom: 10px; }
    .layer p { color: #555; font-size: 16px; }

    .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin-top: 30px; }
    .stat { background: #232F3E; border-radius: 10px; padding: 30px 18px; }
    .stat .num { font-size: 44px; color: #FF9900; font-weight: 700; }
    .stat .label { color: #ccc; font-size: 14px; margin-top: 6px; }

    .punch { font-size: 64px; font-weight: 700; color: #232F3E; line-height: 1.2; }

    .quote {
      background: #FFF8EE; border-left: 6px solid #FF9900;
      padding: 24px 30px; border-radius: 0 12px 12px 0;
      font-size: 24px; color: #444; line-height: 1.6; font-style: italic;
    }
  </style>
</head>
<body>

<div class="reveal">
  <div class="slides">

    <!-- Cover -->
    <section class="cover">
      <h1>__TITLE__<br><span class="accent">__SUBTITLE__</span></h1>
      <div class="subtitle">__TAGLINE__</div>
      <div class="meta">📅 __DATE__ · __AUTHOR__</div>
    </section>

    <!-- Standard slide -->
    <section>
      <h2>__HEADING__</h2>
      <p>...</p>
      <aside class="notes">
        Speaker note: 这页要怎么讲。
      </aside>
    </section>

  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/notes/notes.js"></script>
<script>
  Reveal.initialize({
    hash: true,
    controls: true,
    progress: true,
    center: true,
    transition: 'slide',
    slideNumber: 'c/t',
    plugins: [ RevealNotes ]
  });
</script>

</body>
</html>
```

---

## 红线

- ❌ 不要换 reveal.js 的 base 主题颜色（black / white / league 都行，自定义 CSS 一定 override 死）
- ❌ 不要用 reveal.js 默认的全大写 H 标签（已在 CSS 里 `text-transform: none` 关掉，别忘了）
- ❌ 不要在 cover 上加 reveal 默认 controls（`<section data-state="no-controls">`）
- ❌ 不要用 fragment 当主要表达手段（每页 fragment > 5 个就过度）
- ❌ 同样不要绿 / 紫 / 蓝 偏色

---

## `#html-ppt` vs `#reveal-ppt` 选哪个？

| 场景 | 选 |
|------|----|
| 客户咖啡馆 / 客户电脑 / 不能保证联网 | `#html-ppt` |
| 自己练讲、要 speaker notes 双栏对照 | `#html-ppt` rehearsal |
| 要做 walkthrough 文档（不分页） | `#html-ppt` walkthrough |
| 半正式演讲、可投影 | `#reveal-ppt` |
| 需要 PDF 导出 | `#reveal-ppt` |
| Tech talk 要嵌代码 + 高亮 | `#reveal-ppt` |
| 要 vertical sub-slides 多层下钻 | `#reveal-ppt` |
| 不确定 | `#html-ppt`（默认） |

---

## 用户怎么用

- **基础**：`#reveal-ppt 做一个 X 主题的 deck，10 页`
- **代码 talk**：`#reveal-ppt 做一个 Aza MCP 集成的 tech talk，要带代码高亮`
- **PDF 导出**：`#reveal-ppt 做一个 Q3 plan deck，要能导出 PDF 给同事`
- **vertical 嵌套**：`#reveal-ppt 主线 5 页，每页下面有 2-3 个子页深入`
