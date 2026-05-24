---
name: card-diagram
description: "Generate card-based architecture diagrams as standalone HTML files. Warm glassmorphism style with CSS-only arrows, rounded cards, and backdrop-filter effects. Use when the user asks to create a pipeline, flow, or architecture diagram in card style."
license: MIT
---

# Card-Based Architecture Diagram Generator

Generate beautiful card-based architecture/pipeline diagrams as standalone HTML files. Uses a warm glassmorphism style with CSS-only arrows — no JavaScript, no external dependencies.

## Usage

```
/card-diagram <description of the architecture or pipeline>
```

Examples:
```
/card-diagram A CI/CD pipeline with build, test, deploy, and monitor stages
/card-diagram ML training pipeline: data prep → feature engineering → training → evaluation → deploy
/card-diagram Microservices: API Gateway → Auth → User Service → DB, with async events to Analytics
```

## Output

The skill produces a single self-contained HTML file:
- `~/tmp/<name>-diagram.html` — Standalone, no dependencies, opens in any browser

Then copies to `~/cls-laptop/` and generates an S3 pre-signed URL for sharing.

## Style Specification

### Design Principles

1. **Warm color palette** — cream, amber, terracotta, olive (no cold blues/grays)
2. **Glassmorphism** — `backdrop-filter: blur(6px)` + semi-transparent backgrounds
3. **CSS-only arrows** — `::before` (line) + `::after` (triangle), no SVG
4. **Rounded cards** — `border-radius: 12-18px`
5. **Soft shadows** — subtle box-shadow, no harsh edges
6. **No JavaScript** — pure HTML + CSS
7. **No emojis** — clean typography only

### Color System

Each stage gets a unique warm tone. Define as CSS variables:

```css
:root {
  --bg: #fdf8f0;          /* page background */
  --ink: #2d1b0e;          /* primary text */
  --muted: #6b4423;        /* secondary text */

  /* Per-stage colors (bg, card, border, text) */
  --s1-bg: #faf1e0; --s1-card: #f5e3c4; --s1-border: #c9994e; --s1-text: #6b4910;
  --s2-bg: #ffeed6; --s2-card: #ffd8a6; --s2-border: #e07a3c; --s2-text: #7a3a0c;
  --s3-bg: #fbe5dc; --s3-card: #f5c8b8; --s3-border: #c47057; --s3-text: #6b2e1e;
  --s4-bg: #f9efcf; --s4-card: #f0dca0; --s4-border: #b08842; --s4-text: #5e4514;
  --s5-bg: #e8f0e4; --s5-card: #d4e8cc; --s5-border: #6b9e5a; --s5-text: #3a5e2e;
  --s6-bg: #e8e4f0; --s6-card: #d4cce8; --s6-border: #7a5e9e; --s6-text: #4a2e6b;

  /* Arrow colors match source stage border */
  --arrow-1: #c9994e;
  --arrow-2: #e07a3c;
  --arrow-3: #c47057;
  --arrow-4: #b08842;
  --arrow-5: #6b9e5a;
}
```

For more than 6 stages, cycle through the palette.

### Layout Structure

```
┌────────────────────────────────────────────────────────────┐
│                    Title + Subtitle                          │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  [Block 1] → [Block 2] → [Block 3] → [Block 4]            │
│                                                              │
├────────────────────────────────────────────────────────────┤
│              Additional Sections (modes, tech, etc.)          │
├────────────────────────────────────────────────────────────┤
│                         Legend                                │
└────────────────────────────────────────────────────────────┘
```

### Top Row: Pipeline Blocks

Use CSS Grid with arrow columns between blocks:

```css
.row-top {
  display: grid;
  grid-template-columns: 1fr 50px 1fr 50px 1fr 50px 1fr; /* N blocks + N-1 arrows */
  align-items: stretch;
}
```

For 3 stages: `1fr 50px 1fr 50px 1fr`
For 5 stages: `1fr 50px 1fr 50px 1fr 50px 1fr 50px 1fr`

### Block Component

```html
<div class="block s1">
  <h2>1. Stage Name</h2>
  <div class="card"><div class="title">Component</div><div class="body">Description line 1<br>Description line 2</div></div>
  <div class="card"><div class="title">Component 2</div><div class="body">Details</div></div>
  <div class="scope">Output: path/to/output</div>
</div>
```

```css
.block {
  border-radius: 18px;
  padding: 20px 18px 22px;
  border: 1.5px solid;
  box-shadow: 0 2px 6px rgba(120, 60, 20, 0.06);
}
.card {
  border-radius: 12px;
  padding: 10px 12px;
  margin-bottom: 8px;
  border: 1px solid rgba(0,0,0,0.04);
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
```

### Arrow Component (CSS-only)

```html
<div class="arrow-col"><div class="arrow-h a1"></div></div>
```

```css
.arrow-col {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 12px 0;
}
.arrow-h {
  position: relative;
  width: 100%;
  height: 22px;
}
.arrow-h::before {
  content: "";
  position: absolute;
  top: 50%;
  left: 4px; right: 14px;
  height: 2.5px;
  background: var(--arrow-c, var(--arrow-1));
  border-radius: 2px;
  transform: translateY(-50%);
}
.arrow-h::after {
  content: "";
  position: absolute;
  top: 50%;
  right: 2px;
  width: 0; height: 0;
  border-left: 10px solid var(--arrow-c, var(--arrow-1));
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  transform: translateY(-50%);
}
```

### "Core" Badge (optional, for primary stage)

```css
.s2::before {
  content: "Core";
  position: absolute; top: -10px; left: 14px;
  background: var(--s2-border);
  color: #fff;
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.08em;
  padding: 3px 9px;
  border-radius: 6px;
  text-transform: uppercase;
}
```

### Additional Sections

**Modes/Variants Grid:**
```css
.modes {
  margin-top: 36px;
  border-radius: 18px;
  padding: 22px 24px;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(160,110,60,0.18);
  backdrop-filter: blur(6px);
}
.modes-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
```

**Tech Stack Row:**
```css
.tech-row {
  margin-top: 36px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.tech-card {
  border-radius: 14px;
  padding: 16px 18px;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(160,110,60,0.18);
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  backdrop-filter: blur(6px);
}
```

### Legend

```css
.legend {
  margin-top: 32px;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 18px;
  padding: 14px 20px;
  border: 1px solid rgba(160,110,60,0.2);
  border-radius: 12px;
  background: rgba(255,255,255,0.55);
  backdrop-filter: blur(6px);
}
```

### Page Background

```css
body {
  background: var(--bg);
  background-image:
    radial-gradient(ellipse at top, rgba(255, 220, 180, 0.35), transparent 60%),
    radial-gradient(ellipse at bottom, rgba(240, 220, 160, 0.25), transparent 60%);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
}
```

### Typography

| Element | Size | Weight |
|---------|------|--------|
| Page title | 30px | 700 |
| Subtitle | 14px | 400 |
| Block heading | 14px | 700 |
| Card title | 12.5px | 600 |
| Card body | 11px | 400 |
| Scope line | 11px | 400, italic |
| Section heading | 16px | 700 |
| Tech card heading | 13px | 700 |
| Tech card items | 12px | 400 |
| Legend text | 12px | 400 |

## Workflow

### Step 1: Understand the Architecture

From the user's description, identify:
- How many stages/phases are there? (determines grid columns)
- What are the key components within each stage? (becomes cards)
- What is the output of each stage? (becomes scope line)
- Is there a "core" or primary stage? (gets badge)
- Are there variants/modes? (becomes modes section)
- What are the key technologies? (becomes tech row)

### Step 2: Map to Color Palette

Assign stage colors (s1 through s6) in order. If more than 6 stages, cycle or extend the palette with additional warm hues.

### Step 3: Generate HTML

Produce a single self-contained HTML file with:
- All CSS in a `<style>` block (no external files)
- Semantic HTML structure
- Responsive grid layout
- No JavaScript

### Step 4: Deliver

1. Write to `~/tmp/<name>-diagram.html`
2. Copy to `~/cls-laptop/` for S3 sync
3. Upload to S3: `aws s3 cp ~/tmp/<name>-diagram.html s3://cls-laptop/diagrams/`
4. Generate pre-signed URL: `aws s3 presign s3://cls-laptop/diagrams/<name>-diagram.html --expires-in 900 --region us-west-2`
5. Show the URL to the user

## Adaptation Guidelines

- **2-3 stages**: Use wider blocks, fewer columns
- **5+ stages**: Use narrower blocks or split into two rows
- **Vertical flow**: Replace `grid-template-columns` with `grid-template-rows` and use vertical arrows
- **Sub-pipelines**: Nest blocks inside a larger container with its own background
- **Parallel stages**: Show multiple blocks at the same level without arrows between them

## Complete Template

Below is the minimal boilerplate. Adjust the number of blocks, cards, and sections based on the architecture:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{TITLE}</title>
<style>
  :root { /* color variables */ }
  * { box-sizing: border-box; }
  body { /* page styles */ }
  h1 { /* title */ }
  .subtitle { /* subtitle */ }
  .canvas { max-width: 1320px; margin: 0 auto; }
  .row-top { /* grid */ }
  .block { /* stage block */ }
  .card { /* component card */ }
  .arrow-col { /* arrow container */ }
  .arrow-h { /* arrow line + head */ }
  .s1, .s2, .s3... { /* per-stage colors */ }
  .modes { /* variants section */ }
  .tech-row { /* tech cards */ }
  .legend { /* bottom legend */ }
</style>
</head>
<body>
  <h1>{TITLE}</h1>
  <p class="subtitle">{SUBTITLE}</p>
  <div class="canvas">
    <div class="row-top">
      <!-- blocks + arrows -->
    </div>
    <!-- optional: modes, tech, legend -->
  </div>
</body>
</html>
```
