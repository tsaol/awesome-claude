---
inclusion: manual
---

# Reveal.js PPT Skill

> Invoke with `#reveal-ppt` + your topic. Generates a reveal.js presentation with Amazon brand theme.
>
> Reference: `GlobalOperation/growth/framework-comparison/reveal-demo/index.html`

---

## Positioning

reveal.js is the most mature HTML presentation framework. **Single HTML file + reveal.js from CDN**.

**When to use this over `#html-ppt`**:
- Need fancy transitions (slide / fade / zoom / convex)
- Need vertical sub-slides for deep-dive structure
- Need PDF export (`?print-pdf` built-in)
- Need code highlighting (highlight.js built-in)
- Need presenter mode (press S for separate speaker window)
- Tech talk audience expects "professional slides" feel

**When NOT to use** (use `#html-ppt` instead):
- Must work offline / no network
- Client site with restricted network
- One-shot disposable deck
- Need rehearsal timer + notes inline

---

## Core Principles

1. **Viewport Fitting** — Content must fit within viewport. Never allow slide scrolling.
2. **Distinctive Design** — Avoid generic reveal.js defaults. Apply Amazon brand or custom style.
3. **Content Density** — Max 5 bullets per slide, max 10 lines of code per code slide.

### Content Density Limits

| Slide Type | Maximum Content |
|---|---|
| Title | 1 heading + 1 subtitle |
| Content | 1 heading + 4-5 points |
| Code | 1 heading + 8-10 lines |
| Comparison | 2 columns, 4 items each |
| Quote | 1 quote (3 lines max) + attribution |

**Overflows? Split into sub-slides (vertical sections).**

---

## Your Task

When user invokes `#reveal-ppt`:

### Step 1: Confirm

1. **Topic / content outline**
2. **Slide count** (default 8-12)
3. **Code snippets?** (determines highlight plugin)
4. **PDF export needed?** (determines export instructions)
5. **Style** — Amazon Brand (default) or Custom mood

### Step 2: Generate Single HTML File

Structure:
```html
<!DOCTYPE html>
<head>
  <link rel="stylesheet" href="...reveal.css">
  <link rel="stylesheet" href="...theme/black.css">
  <style>__BRAND_OVERRIDES__</style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <section>...</section>
      <section>
        <section>...</section>  <!-- vertical sub-slide -->
      </section>
    </div>
  </div>
  <script src="...reveal.js"></script>
  <script>Reveal.initialize({ ... });</script>
</body>
```

### Step 3: Amazon Brand Theme (default)

Same color palette as `#html-ppt`:
- Orange `#FF9900` / Deep orange `#c45500`
- Dark blue `#232F3E` / Light orange `#FFF8EE` / Border `#FFE0B2`
- Font: `-apple-system, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif`

Override reveal.js defaults:
```css
:root {
  --r-main-color: #1a1a1a;
  --r-heading-color: #232F3E;
  --r-link-color: #FF9900;
  --r-background-color: #fff;
}
.reveal { font-family: ...; color: #1a1a1a; }
.reveal h1, .reveal h2 { color: #232F3E; text-transform: none; }
.reveal .accent { color: #FF9900; }
```

### Step 4: reveal.js Features (use as needed)

**Speaker notes**:
```html
<section>
  <h2>...</h2>
  <aside class="notes">How to present this slide.</aside>
</section>
```
Press `S` for presenter mode (separate window with notes + timer + next slide).

**Vertical sub-slides** (drill-down):
```html
<section>
  <section><h2>Main Topic</h2></section>
  <section><p>Detail 1</p></section>
  <section><p>Detail 2</p></section>
</section>
```

**Fragments** (incremental reveal):
```html
<ul>
  <li class="fragment">First point</li>
  <li class="fragment">Second point</li>
</ul>
```
Max 5 fragments per slide.

**Code blocks**:
```html
<pre><code class="hljs python" data-trim>
def hello():
    print("world")
</code></pre>
```

### Step 5: Standard Init Config

```javascript
Reveal.initialize({
  hash: true,
  controls: true,
  progress: true,
  center: true,
  transition: 'slide',
  slideNumber: 'c/t',
  plugins: [ RevealNotes ]
});
```

If code highlighting needed, add:
```javascript
plugins: [ RevealNotes, RevealHighlight ]
```
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/monokai.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/highlight.js"></script>
```

### Step 6: Output

Generate `<topic>-reveal.html`, give `open` command, list shortcuts:
- Arrow keys: navigate
- `S`: speaker mode
- `F`: fullscreen
- `O`: overview
- `B`: blackout
- `?`: all shortcuts

PDF export: append `?print-pdf` to URL, then browser Print > Save as PDF.

---

## PPT Conversion

When user provides a .pptx:
1. Run `python scripts/extract-pptx.py <input.pptx> <output_dir>`
2. Show extracted slides for confirmation
3. Convert to reveal.js format preserving text, images, notes

---

## PDF Export (Screenshot-based)

For higher quality PDF than browser print:
```bash
bash scripts/export-pdf.sh <path-to-html> [output.pdf] [--compact]
```

---

## Layout Blocks

Same CSS classes as `#html-ppt` (layers, stats, quote, punch, compare) can be used inside reveal `<section>` elements.

---

## Red Lines

- Do NOT change reveal.js base theme colors without CSS override (always override)
- Do NOT use reveal.js default uppercase headings (`text-transform: none` in CSS)
- Do NOT use fragment as main expression method (max 5 per slide)
- Do NOT use green / purple / blue accent colors in Amazon brand mode
- Do NOT allow horizontal scrolling in any slide
- Do NOT exceed content density limits

---

## Skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>__TITLE__</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/black.css" id="theme">
  <style>
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

    .cover { background: linear-gradient(135deg, #232F3E 0%, #0d1421 100%) !important; }
    .cover h1 { color: #fff !important; }
    .cover .subtitle { color: #ccc; font-size: 0.6em; margin-top: 20px; }

    .layers { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 30px; }
    .layer { background: #FFF8EE; border: 2px solid #FFE0B2; border-radius: 12px; padding: 24px; }
    .layer .ln { font-size: 14px; color: #c45500; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; }
    .layer h4 { color: #232F3E; font-size: 22px; margin-bottom: 10px; }

    .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin-top: 30px; }
    .stat { background: #232F3E; border-radius: 10px; padding: 30px 18px; }
    .stat .num { font-size: 44px; color: #FF9900; font-weight: 700; }
    .stat .label { color: #ccc; font-size: 14px; margin-top: 6px; }

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
    <section class="cover">
      <h1>__TITLE__<br><span class="accent">__SUBTITLE__</span></h1>
      <div class="subtitle">__TAGLINE__</div>
    </section>

    <section>
      <h2>__HEADING__</h2>
      <p>...</p>
      <aside class="notes">Speaker note here.</aside>
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

## When to Use Which Skill

| Scenario | Choose |
|----------|--------|
| Offline / client site / no network | `#html-ppt` |
| Rehearsal with inline notes + timer | `#html-ppt` rehearsal |
| Scrollable document (no pagination) | `#html-ppt` walkthrough |
| Formal talk with transitions | `#reveal-ppt` |
| PDF export needed | `#reveal-ppt` |
| Tech talk with code highlighting | `#reveal-ppt` |
| Vertical sub-slide drill-down | `#reveal-ppt` |
| Not sure | `#html-ppt` (default) |

---

## Usage Examples

- `#reveal-ppt Make a tech talk about MCP integration, 12 slides with code`
- `#reveal-ppt Convert quarterly-plan.pptx to web slides`
- `#reveal-ppt Internal demo of our RAG pipeline, need PDF export`
