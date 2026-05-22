---
inclusion: manual
---

# HTML PPT Skill — 手搓单文件 deck

> 调用方式：在聊天里输入 `#html-ppt` + 你的内容主题，我会按 Cao Liu 的固定风格生成一个单文件 HTML deck（无外部依赖，双击即开）。
>
> 参考样本：
> - `GlobalOperation/growth/amazon-growth-design-rehearsal.html`（完整 19 页彩排版）
> - `GlobalOperation/growth/amazon-growth-design-walkthrough.html`（可滚动文档版）
> - `HR/AZA/presentations/html/shein_agent_review_slide.html`（单页 1280×720 slide）

---

## 这个 skill 的定位

不是 reveal.js / Slidev / Spectacle 这些框架。是**手搓的单 HTML 文件**，零依赖、零联网、零安装，双击就开。

**适用场景**：
- 自己练讲（rehearsal）
- 给 BD / 同事内部传阅
- 要在客户现场打开但又不能保证联网
- 一次性 deck，不想维护

**不适用场景**：
- 需要复杂动画 / 过场效果
- 需要嵌入复杂 React 组件 / 实时 demo
- 团队多人协作长期维护

那些场景用 `#reveal-ppt` 这个 skill。

---

## 你的任务

当用户调用 `#html-ppt` 时，按下面的步骤生成 deck。

### Step 1: 确认意图

先问清楚（如果用户没说全）：

1. **主题 / 内容**是什么？
2. **deck 类型**是哪种：
   - `rehearsal` — 给自己练讲，每页带 speaker notes（黑底右栏，按 N 切换）
   - `walkthrough` — 内部消化文档，可滚动长页（不分页）
   - `slide-deck` — 多页演示，键盘翻页
   - `single-slide` — 单页 1280×720 海报式
3. **目标受众**（决定语气）：自己 / 团队 / 客户
4. **页数 / 章节**：用户给章节我才能定页数

如果用户说"按你看着办"，默认走 `slide-deck` + 8–12 页。

### Step 2: 选 layout 模板

每个 deck 由这些 layout 组合：

| Layout | 用途 | 例子 |
|--------|------|------|
| **cover** | 封面 | 标题 + 副标题 + meta 行 |
| **section-title** | 章节分隔 | 大字 + eyebrow tag |
| **bullet** | 要点列表 | 标题 + 3–5 条 ul |
| **layers** | 三栏 / 三层模型 | 三个橙底 box（mental model） |
| **stats** | 数据展示 | 4 个深蓝卡 + 橙数字 |
| **flow** | 流程步骤 | 编号圆圈 + 标题 + 描述 |
| **compare** | 两栏对比 | A vs B 双 box |
| **quote** | 引言 / 客户原话 | 浅橙底 + 橙左边线 |
| **callout** | 关键 takeaway | 深蓝底白字框 |
| **punch-line** | 大字结论 | 60–64px，可双色高亮 |
| **schedule** | 时间表 / 议程 | 深蓝表头表格 |
| **bezos-style** | 名言页 | 黑底渐变 + 引言 |
| **end** | 结束页 | "Ready / 谢谢 / Q&A" |

不要凭空发明 layout。混用上面这些就够。

### Step 3: 套用品牌样式（强制）

**色板（必须用）**：
- `#FF9900` — Amazon 橙，accent / highlight / 数字 / 链接
- `#c45500` — 深橙，eyebrow / tag 文字
- `#232F3E` — Amazon 深蓝，标题 / 深色背景 / 卡
- `#FFF8EE` — 浅橙底，layers / quote
- `#FFE0B2` — 橙边线
- `#fff / #1a1a1a / #333 / #555 / #666 / #888 / #ccc` — 中性色阶

**字体（必须用）**：
```css
font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
```

**顶部 6px 渐变条（每个 deck 必有）**：
```css
.top-bar {
  height: 6px;
  background: linear-gradient(90deg, #FF9900 0%, #232F3E 100%);
}
```

**圆角统一**：8px / 10px / 12px，不要其他值。

**字号阶梯**：
- 封面 H1: 56px
- 普通 H2: 44px
- H3: 24px
- 正文: 22px（slide）/ 14px（walkthrough）
- punch-line: 60–64px
- eyebrow: 13px，全大写，letter-spacing 2px

### Step 4: 交互层（slide-deck 和 rehearsal 必须有）

```javascript
// 必备
- ← / → / Space / PageUp / PageDown 翻页
- Home / Esc 回首页
- End 跳最后一页

// rehearsal 额外
- N 切换 speaker notes（body 加 .show-notes class）
- T 启停计时器（右下角显示 mm:ss）
- R 重置计时器
- 进度条（顶部 2px，按页数比例填充）
- 页码 (1 / N)
- 点击空白翻页
```

代码骨架放在最下面"通用脚手架"那一节，直接改不要重写。

### Step 5: Speaker notes 写法（rehearsal 类型才有）

每张 slide 的 notes 必须包含：

1. **How to say it** — 这页要怎么开口讲（一段话）
2. **关键停顿点** — 哪里要停、哪里要加重
3. **可能的延伸问题** — 客户可能问什么，怎么接
4. **红线** — 这页最容易踩的错（不要说什么）

不要把 notes 当 cheat sheet。它是"演练剧本"。

### Step 6: 输出

不要先解释，**直接生成完整 HTML 文件**。文件路径放在用户指定的目录下，命名：

- `<topic>-rehearsal.html` （彩排版）
- `<topic>-walkthrough.html` （文档版）
- `<topic>-deck.html` （演示版）
- `<topic>-slide.html` （单页）

生成完毕后，给用户一行 `open` 命令直接打开，再给 3–5 个使用提示（按键 / 注意事项）。

---

## 通用脚手架（直接复用，不要重写）

### Slide-deck / Rehearsal 骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
    background: #1a1a1a; color: #fff;
    overflow: hidden; height: 100vh;
  }
  .deck { position: relative; width: 100vw; height: 100vh; }
  .slide {
    position: absolute; top: 0; left: 0;
    width: 100%; height: 100%;
    display: none;
    background: #fff; color: #1a1a1a;
  }
  .slide.active { display: flex; flex-direction: column; }
  .top-bar { height: 6px; background: linear-gradient(90deg, #FF9900 0%, #232F3E 100%); }
  .slide-body { flex: 1; display: flex; overflow: hidden; }
  .slide-main {
    flex: 1; padding: 60px 80px 40px;
    display: flex; flex-direction: column; justify-content: center;
    overflow: auto;
  }
  .slide.has-notes .slide-main { flex: 1.6; }
  .slide-notes {
    flex: 1; background: #232F3E; color: #fff;
    padding: 60px 50px 40px; overflow: auto;
    display: none;
  }
  body.show-notes .slide.has-notes .slide-notes { display: block; }

  .eyebrow {
    font-size: 13px; color: #FF9900; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px;
    margin-bottom: 16px;
  }
  .slide h2 {
    font-size: 44px; font-weight: 700; color: #232F3E;
    line-height: 1.15; letter-spacing: -0.5px;
    margin-bottom: 24px;
  }
  .slide p { font-size: 22px; color: #333; line-height: 1.6; margin-bottom: 16px; }
  .slide ul { font-size: 22px; color: #333; line-height: 1.7; margin-left: 28px; margin-bottom: 16px; }
  .slide .accent { color: #FF9900; font-weight: 700; }

  .controls {
    position: fixed; bottom: 20px; right: 24px;
    display: flex; gap: 12px; align-items: center;
    background: rgba(35, 47, 62, 0.92); color: #fff;
    padding: 8px 16px; border-radius: 24px;
    font-size: 13px; z-index: 100;
  }
  .controls .counter { color: #FF9900; font-weight: 700; }
  .progress {
    position: fixed; top: 6px; left: 0; height: 2px;
    background: #FF9900; transition: width 0.3s ease;
    z-index: 99;
  }

  /* === LAYOUT BLOCKS === */
  .layers { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 30px; }
  .layer { background: #FFF8EE; border: 2px solid #FFE0B2; border-radius: 12px; padding: 24px; }
  .layer .ln { font-size: 12px; color: #c45500; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; }

  .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin-top: 24px; }
  .stat { background: #232F3E; border-radius: 10px; padding: 26px 18px; text-align: center; }
  .stat .num { font-size: 40px; color: #FF9900; font-weight: 700; line-height: 1; }
  .stat .label { font-size: 13px; color: #ccc; margin-top: 8px; }

  .quote {
    background: #FFF8EE; border-left: 6px solid #FF9900;
    padding: 24px 30px; margin-top: 24px;
    border-radius: 0 12px 12px 0;
    font-size: 22px; color: #444; line-height: 1.6; font-style: italic;
  }

  .punch-line {
    font-size: 64px; font-weight: 700; color: #232F3E;
    line-height: 1.2; letter-spacing: -1px;
  }
</style>
</head>
<body>

<div class="progress" id="progress"></div>

<div class="deck" id="deck">
  <!-- SLIDES GO HERE -->
</div>

<div class="controls">
  <span class="counter"><span id="cur">1</span> / <span id="total">__TOTAL__</span></span>
  <span class="timer" id="timer">00:00</span>
</div>

<script>
  const slides = document.querySelectorAll('.slide');
  const total = slides.length;
  document.getElementById('total').textContent = total;
  let cur = 0;

  function show(i) {
    if (i < 0) i = 0;
    if (i >= total) i = total - 1;
    slides[cur].classList.remove('active');
    slides[i].classList.add('active');
    cur = i;
    document.getElementById('cur').textContent = i + 1;
    document.getElementById('progress').style.width = ((i + 1) / total * 100) + '%';
  }
  show(0);

  document.addEventListener('keydown', (e) => {
    if (['ArrowRight', ' ', 'PageDown'].includes(e.key)) { e.preventDefault(); show(cur + 1); }
    else if (['ArrowLeft', 'PageUp'].includes(e.key)) { e.preventDefault(); show(cur - 1); }
    else if (e.key === 'Home' || e.key === 'Escape') show(0);
    else if (e.key === 'End') show(total - 1);
    else if (e.key === 'n' || e.key === 'N') document.body.classList.toggle('show-notes');
    else if (e.key === 't' || e.key === 'T') toggleTimer();
    else if (e.key === 'r' || e.key === 'R') resetTimer();
  });

  let timerInterval = null, timerStart = 0, timerElapsed = 0;
  function toggleTimer() {
    if (timerInterval) {
      clearInterval(timerInterval); timerInterval = null;
      timerElapsed += Date.now() - timerStart;
    } else {
      timerStart = Date.now();
      timerInterval = setInterval(updateTimer, 1000);
    }
  }
  function resetTimer() {
    clearInterval(timerInterval); timerInterval = null; timerElapsed = 0;
    document.getElementById('timer').textContent = '00:00';
  }
  function updateTimer() {
    const t = timerElapsed + (Date.now() - timerStart);
    const m = Math.floor(t / 60000), s = Math.floor((t % 60000) / 1000);
    document.getElementById('timer').textContent = String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
  }

  document.addEventListener('click', (e) => {
    if (e.target.closest('.controls')) return;
    if (e.target.closest('.slide-notes')) return;
    show(cur + 1);
  });
</script>

</body>
</html>
```

### Slide 模板

```html
<!-- Cover -->
<div class="slide slide-cover">
  <div class="top-bar"></div>
  <div class="slide-body">
    <div class="slide-main" style="background: linear-gradient(135deg, #232F3E 0%, #0d1421 100%); color: #fff;">
      <h1 style="font-size: 56px; color: #fff;">__TITLE__<br><span class="accent">__SUBTITLE__</span></h1>
      <div style="font-size: 20px; color: #ccc; margin-top: 24px;">__TAGLINE__</div>
      <div style="font-size: 14px; color: #888; border-top: 1px solid #333; padding-top: 16px; margin-top: 30px;">📅 __DATE__ · __AUTHOR__</div>
    </div>
  </div>
</div>

<!-- Bullet w/ notes -->
<div class="slide has-notes">
  <div class="top-bar"></div>
  <div class="slide-body">
    <div class="slide-main">
      <div class="eyebrow">__EYEBROW__</div>
      <h2>__HEADING__</h2>
      <ul>
        <li>__POINT_1__</li>
        <li>__POINT_2__</li>
      </ul>
    </div>
    <div class="slide-notes">
      <h4 style="color: #FF9900; text-transform: uppercase; letter-spacing: 2px; font-size: 14px; margin-bottom: 14px;">How to say it</h4>
      <p style="font-size: 16px; color: #ddd; line-height: 1.7;">__NOTES__</p>
    </div>
  </div>
</div>

<!-- Punch line -->
<div class="slide has-notes">
  <div class="top-bar"></div>
  <div class="slide-body">
    <div class="slide-main">
      <div class="eyebrow">__EYEBROW__</div>
      <div class="punch-line">__LINE_1__<br><span class="accent">__HIGHLIGHT__</span><br>__LINE_2__</div>
    </div>
    <div class="slide-notes">...</div>
  </div>
</div>
```

### Walkthrough（可滚动文档版）骨架

参考 `GlobalOperation/growth/amazon-growth-design-walkthrough.html`，区别：
- 不分页，max-width 980px 居中
- 每个 section 是白底圆角卡，间隔 24px
- 顶部有 TOC 锚点跳转
- 整体在 `#f7f7f7` 灰底上

---

## 红线

不要做这些：

- ❌ 引入任何外部 CDN / npm 包（这个 skill 的灵魂就是单文件零依赖）
- ❌ 用绿色 / 紫色 / 蓝色（除了导航 link）—— 严格 Amazon 橙 + 深蓝
- ❌ 用 emoji 当装饰（数字 / icon 用 SVG 或 unicode 几何符号）
- ❌ 单页超过 5 个要点（信息过载）
- ❌ 字号小于 14px（slide）/ 12px（walkthrough）
- ❌ 不写 speaker notes 的 rehearsal deck
- ❌ 用 `<table>` 做布局（用 grid / flex）

---

## 用户怎么用

- **基础**：`#html-ppt 给我做一个 X 主题的 deck，用 rehearsal 风格，10 页`
- **指定参考**：`#html-ppt 参考 amazon-growth-design-rehearsal.html 的风格做一个 Y 主题`
- **改造**：`#html-ppt 把 X.md 转成 walkthrough HTML`
- **快速 punch line**：`#html-ppt 给我做一张单页 punch-line slide，内容是 ...`
- **指定章节**：`#html-ppt 内容大纲：1) ... 2) ... 3) ...`
