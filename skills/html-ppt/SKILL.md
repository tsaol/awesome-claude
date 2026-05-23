---
inclusion: manual
---

# HTML PPT Skill

> Invoke with `#html-ppt` + your topic. Generates a single-file HTML deck with zero dependencies.
>
> Reference samples:
> - `GlobalOperation/growth/amazon-growth-design-rehearsal.html`
> - `GlobalOperation/growth/amazon-growth-design-walkthrough.html`
> - `HR/AZA/presentations/html/shein_agent_review_slide.html`

---

## Positioning

Not reveal.js / Slidev / Spectacle. **A hand-crafted single HTML file** — zero dependencies, zero network, double-click to open.

**Good for**: rehearsal, internal sharing, offline presentations, one-shot decks.
**Not for**: complex animations, React components, long-term team maintenance. Use `#reveal-ppt` for those.

---

## Detect Mode

Determine what the user wants:

- **Mode A: New Presentation** — Create from scratch. Go to Step 1.
- **Mode B: PPT Conversion** — Convert a .pptx file. Go to PPT Conversion section.
- **Mode C: Enhancement** — Improve an existing HTML presentation. Follow Mode C rules below.

### Mode C: Modification Rules

When enhancing existing presentations, viewport fitting is the biggest risk:

1. **Before adding content:** Count existing elements, check against density limits
2. **Adding images:** Must have `max-height: min(50vh, 400px)`. If slide already has max content, split into two slides
3. **Adding text:** Max 4-5 bullets per slide. Exceeds limits? Split into continuation slides
4. **After ANY modification, verify:** `.slide` has `overflow: hidden`, new elements use `clamp()`, images have viewport-relative max-height, content fits at 1280x720
5. **Proactively reorganize:** If modifications will cause overflow, automatically split content and inform the user. Don't wait to be asked

**When adding images to existing slides:** Move image to new slide or reduce other content first. Never add images without checking if existing content already fills the viewport.

---

## Core Principles

1. **Zero Dependencies** — Single HTML file, all CSS/JS inline. No npm, no CDN.
2. **Viewport Fitting (NON-NEGOTIABLE)** — Every slide MUST fit exactly in 100vh. No scrolling within slides. Content overflows? Split into multiple slides.
3. **Distinctive Design** — Avoid generic "AI slop." Choose fonts and colors that feel custom-crafted.
4. **Show, Don't Tell** — When user is unsure of style, generate visual previews (save to `~/tmp/slide-previews/`).

---

## Viewport Fitting Rules

These apply to EVERY slide:

- Every `.slide` must have `height: 100vh; height: 100dvh; overflow: hidden;`
- ALL font sizes and spacing must use `clamp(min, preferred, max)` — never fixed px alone
- Include the full contents of [viewport-base.css](viewport-base.css) in every presentation
- Include `prefers-reduced-motion` support
- Never negate CSS functions directly (`-clamp()` is silently ignored) — use `calc(-1 * clamp(...))`

### Content Density Limits Per Slide

| Slide Type | Maximum Content |
|---|---|
| Title/Cover | 1 heading + 1 subtitle + optional tagline |
| Bullet | 1 heading + 4-5 bullet points |
| Layers/Grid | 1 heading + 3 cards (3-column grid) |
| Stats | 1 heading + 4 stat boxes |
| Quote | 1 quote (max 3 lines) + attribution |
| Punch-line | 1 large text block (2-3 lines) |
| Code | 1 heading + 8-10 lines of code |

**Content exceeds limits? Split into multiple slides. Never cram, never scroll.**

---

## Your Task

When user invokes `#html-ppt`:

### Step 1: Confirm Intent

Ask (if not already specified):

1. **Topic / content** — What is this about?
2. **Deck type**:
   - `rehearsal` — Speaker notes in dark right panel, timer (N to toggle notes, T for timer)
   - `walkthrough` — Scrollable long-page document (no pagination)
   - `slide-deck` — Multi-page presentation with keyboard navigation
   - `single-slide` — Single 1280x720 poster slide
3. **Target audience** — Self / team / client (determines tone)
4. **Slide count / sections** — Default: 8-12 slides

If user says "up to you", default to `slide-deck` + 8-12 slides.

### Step 2: Choose Style

Ask user's style preference:

**Option A: Amazon Brand** — Orange + dark blue, professional corporate. Skip to Step 3.
**Option B: Pick a preset** — Choose from 12 curated presets directly. See [STYLE_PRESETS.md](STYLE_PRESETS.md).
**Option C: Show me options (recommended for custom)** — Generate 3 visual previews based on mood.

#### "Show me options" flow:

1. Ask the mood: Impressed/Confident | Excited/Energized | Calm/Focused | Inspired/Moved
2. Based on mood, pick 3 presets from the mood-to-preset table in [STYLE_PRESETS.md](STYLE_PRESETS.md)
3. Generate 3 single-slide HTML preview files (one per preset) showing title slide with typography, colors, animation
4. Save previews to `~/tmp/slide-previews/` (style-a.html, style-b.html, style-c.html)
5. Open each preview for the user
6. Ask which they prefer: Style A / Style B / Style C / Mix elements

Each preview should be ~50-100 lines, self-contained, showing one animated title slide with the preset's exact fonts, colors, and signature elements.

#### "Pick a preset" flow:

User names a preset directly (e.g., "Bold Signal", "Neon Cyber"). Read [STYLE_PRESETS.md](STYLE_PRESETS.md) for specs and generate using those exact fonts, colors, and signature elements.

If user says "up to you" or doesn't specify, default to Amazon Brand.

### Step 3: Amazon Brand Style (when applicable)

**Colors (required for Amazon brand)**:
- `#FF9900` — Amazon orange, accent / highlight / numbers
- `#c45500` — Deep orange, eyebrow / tag text
- `#232F3E` — Amazon dark blue, headings / dark backgrounds
- `#FFF8EE` — Light orange background for layers/quotes
- `#FFE0B2` — Orange borders
- `#fff / #1a1a1a / #333 / #555 / #666 / #888 / #ccc` — Neutral scale

**Font**:
```css
font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
```

**Top 6px gradient bar (every deck must have)**:
```css
.top-bar { height: 6px; background: linear-gradient(90deg, #FF9900 0%, #232F3E 100%); }
```

**Border radius**: 8px / 10px / 12px only.

**Font size ladder**:
- Cover H1: 56px → `clamp(2rem, 5vw, 3.5rem)`
- H2: 44px → `clamp(1.5rem, 3.5vw, 2.75rem)`
- Body: 22px → `clamp(0.9rem, 1.8vw, 1.375rem)`
- Punch-line: 60-64px → `clamp(2.5rem, 6vw, 4rem)`
- Eyebrow: 13px, uppercase, letter-spacing 2px

### Step 4: Layout Building Blocks

| Layout | Use | Description |
|--------|-----|-------------|
| **cover** | Opening | Title + subtitle + meta line |
| **section-title** | Chapter divider | Large text + eyebrow tag |
| **bullet** | Key points | Heading + 3-5 ul items |
| **layers** | 3-column model | Three colored boxes (mental model) |
| **stats** | Data display | 4 dark-blue cards with orange numbers |
| **flow** | Process steps | Numbered circles + title + description |
| **compare** | Two-column contrast | A vs B dual boxes |
| **quote** | Citation | Light orange background + orange left border |
| **callout** | Key takeaway | Dark-blue background white text |
| **punch-line** | Big conclusion | 60-64px, dual-color highlight |
| **table-wrap** | Data table | Dark header, clean rows |
| **timeline** | Chronological | Left-line with dots and items |
| **schedule** | Agenda / timeline | Dark header table |
| **end** | Closing | "Questions?" / thank you / CTA |

Do not invent new layouts. Mix these blocks.

### Step 5: Interaction Layer (slide-deck and rehearsal)

```javascript
// Required:
// ← / → / Space / PageDown: next/prev
// Home / Esc: first slide
// End: last slide
// Click: next slide (except on controls/dots)
// Nav dots (right side, active dot highlights on slide change, clickable)
// Progress bar (top 2px, proportional fill)
// Page counter (1 / N)

// Rehearsal additional:
// N: toggle speaker notes
// T: start/stop timer
// R: reset timer
```

### Step 6: Speaker Notes (rehearsal only)

Each slide's notes must include:
1. **How to say it** — Opening sentence for this slide
2. **Key pauses** — Where to stop, where to emphasize
3. **Potential questions** — What the audience might ask
4. **Red lines** — What NOT to say on this slide

### Step 7: Output

Generate the complete HTML file directly. Naming:
- `<topic>-rehearsal.html`
- `<topic>-walkthrough.html`
- `<topic>-deck.html`
- `<topic>-slide.html`

After generation, give the user an `open` command and usage tips (keys, notes).

---

## Image Handling

When user provides images for the presentation:

### Step 1: Evaluate Images

1. **Scan** — List all image files (.png, .jpg, .svg, .webp)
2. **View each image** — Use the Read tool (Claude is multimodal)
3. **Evaluate** — For each: what it shows, USABLE or NOT USABLE (with reason), dominant colors
4. **Co-design the outline** — Images inform slide structure alongside text. Don't "plan slides then add images" — design around both from the start

### Step 2: Process Images

```python
from PIL import Image, ImageDraw

# Circular crop (for logos on rounded aesthetics)
def crop_circle(input_path, output_path):
    img = Image.open(input_path).convert('RGBA')
    w, h = img.size
    size = min(w, h)
    left, top = (w - size) // 2, (h - size) // 2
    img = img.crop((left, top, left + size, top + size))
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
    img.putalpha(mask)
    img.save(output_path, 'PNG')

# Resize (for oversized images)
def resize_max(input_path, output_path, max_dim=1200):
    img = Image.open(input_path)
    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    img.save(output_path, quality=85)
```

| Situation | Operation |
|-----------|-----------|
| Square logo on rounded aesthetic | `crop_circle()` |
| Image > 1MB | `resize_max(max_dim=1200)` |
| Wrong aspect ratio | Manual crop with `img.crop()` |

### Step 3: Place Images in HTML

```css
.slide-image {
    max-width: 100%;
    max-height: min(50vh, 400px);
    object-fit: contain;
    border-radius: 8px;
}
.slide-image.screenshot {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.slide-image.logo {
    max-height: min(30vh, 200px);
}
```

**Rules:**
- Use relative file paths (not base64) for images unless embedding a single logo
- Never repeat the same image on multiple slides (except logos on title + closing)
- Adapt border/shadow colors to match the chosen style's accent
- Logo: centered on title slide. Screenshots: two-column layout with text

---

## PPT Conversion

When user provides a .pptx file:

1. Run `python scripts/extract-pptx.py <input.pptx> <output_dir>` (install python-pptx if needed)
2. Show extracted slide titles and image counts for confirmation
3. Ask for style preference (Amazon brand or custom)
4. Generate HTML preserving all text, images, and notes

---

## PDF Export

After generating a deck, offer PDF export:

```bash
bash scripts/export-pdf.sh <path-to-html> [output.pdf] [--compact]
```

- Uses Playwright to screenshot each slide at 1920x1080
- `--compact` flag renders at 1280x720 for smaller files
- Animations are not preserved (static snapshots)

---

## Deploy (Vercel)

After generating a deck, offer deployment for sharing:

```bash
bash scripts/deploy.sh <path-to-html>
```

- Deploys to a live URL that works on any device (phones, tablets, laptops)
- Free hosting via Vercel, no server to maintain
- Single HTML files are auto-wrapped with `index.html`
- Referenced local assets (images, fonts) are bundled automatically

**First-time setup:**
1. Node.js required (`brew install node` or https://nodejs.org)
2. Vercel CLI installs automatically via npx
3. User runs `vercel login` if not already authenticated

**Gotchas:**
- Local images via CSS `background-image` may not be auto-detected; prefer `<img src="...">` or deploy a folder
- Redeploying updates the same URL (no need to share new link)
- Filenames with spaces work but get URL-encoded as `%20`

---

## Animation Patterns

When generating decks, reference [animation-patterns.md](animation-patterns.md) for:
- Entrance animations (fade+slide, scale, blur)
- Background effects (gradient mesh, grid patterns)
- Interactive mouse effects (custom cursor, 3D tilt, magnetic buttons, cursor auto-hide)
- Effect-to-feeling matching table

Use `.reveal` class + Intersection Observer for scroll-triggered animations when building scroll-snap decks.

### Optional Interactive Effects (slide-deck type)

Include these by default unless user opts out or requests minimal:

1. **Cursor auto-hide** — Hide cursor after 3s inactivity (presentation mode feel)
2. **Nav dot hover glow** — Glow + scale on hover for navigation dots
3. **3D tilt on cards** — Cards/panels subtly rotate following mouse position
4. **Magnetic buttons** — Nav dots and CTA buttons attract toward cursor

For techy/futuristic styles (Neon Cyber, Terminal Green), also include:
5. **Custom cursor with trail** — Replace default cursor with styled circle + trail

---

## Supporting Files

| File | Purpose | When to Read |
|------|---------|--------------|
| [STYLE_PRESETS.md](STYLE_PRESETS.md) | 12 curated visual presets with colors, fonts, signatures | Style selection (Step 2) |
| [viewport-base.css](viewport-base.css) | Mandatory responsive CSS | Always (include in every deck) |
| [animation-patterns.md](animation-patterns.md) | Animation reference | When adding motion effects |
| [scripts/extract-pptx.py](scripts/extract-pptx.py) | PPT content extraction | When converting .pptx files |
| [scripts/export-pdf.sh](scripts/export-pdf.sh) | PDF export | When user wants PDF output |
| [scripts/deploy.sh](scripts/deploy.sh) | Deploy to Vercel for sharing | When user wants a live URL |

---

## Red Lines

- Do NOT use external CDN / npm packages (zero-dependency is the soul of this skill)
- Do NOT use green / purple / blue for accent colors in Amazon brand mode
- Do NOT use emoji as decoration (use SVG or unicode geometric symbols)
- Do NOT exceed 5 bullet points per slide
- Do NOT use font sizes below 14px (slide) / 12px (walkthrough)
- Do NOT skip speaker notes in rehearsal decks
- Do NOT use `<table>` for layout (use grid / flex)
- Do NOT use fixed px without responsive clamp() fallback
- Do NOT allow any slide to scroll — split content instead

---

## Skeleton (slide-deck / rehearsal)

```html
<!DOCTYPE html>
<html lang="en">
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
    overflow: hidden;
  }
  .slide.active { display: flex; flex-direction: column; }
  .top-bar { height: 6px; background: linear-gradient(90deg, #FF9900 0%, #232F3E 100%); }
  .slide-body { flex: 1; display: flex; overflow: hidden; }
  .slide-main {
    flex: 1; padding: clamp(1.5rem, 4vw, 60px) clamp(2rem, 6vw, 80px) clamp(1rem, 3vw, 40px);
    display: flex; flex-direction: column; justify-content: center;
    overflow: hidden;
  }
  .slide.has-notes .slide-main { flex: 1.6; }
  .slide-notes {
    flex: 1; background: #232F3E; color: #fff;
    padding: 60px 50px 40px; overflow: auto;
    display: none;
  }
  body.show-notes .slide.has-notes .slide-notes { display: block; }

  .eyebrow {
    font-size: clamp(0.7rem, 1vw, 0.8125rem); color: #FF9900; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px;
    margin-bottom: clamp(0.5rem, 1.5vw, 1rem);
  }
  .slide h2 {
    font-size: clamp(1.5rem, 3.5vw, 2.75rem); font-weight: 700; color: #232F3E;
    line-height: 1.15; letter-spacing: -0.5px;
    margin-bottom: clamp(0.75rem, 2vw, 1.5rem);
  }
  .slide p { font-size: clamp(0.9rem, 1.8vw, 1.375rem); color: #333; line-height: 1.6; margin-bottom: 1rem; }
  .slide ul { font-size: clamp(0.9rem, 1.8vw, 1.375rem); color: #333; line-height: 1.7; margin-left: 28px; margin-bottom: 1rem; }
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

  /* Nav dots */
  .nav-dots {
    position: fixed; right: clamp(1rem, 2vw, 2rem); top: 50%;
    transform: translateY(-50%); z-index: 100;
    display: flex; flex-direction: column; gap: clamp(6px, 1vh, 12px);
  }
  .nav-dot {
    width: clamp(8px, 0.8vw, 12px); height: clamp(8px, 0.8vw, 12px);
    border-radius: 50%; background: rgba(0, 0, 0, 0.2);
    border: none; cursor: pointer;
    transition: all 0.3s ease;
  }
  .nav-dot.active {
    background: #FF9900; transform: scale(1.4);
  }
  @media (max-height: 600px) { .nav-dots { display: none; } }

  /* === LAYOUT BLOCKS === */
  .layers { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: clamp(0.75rem, 1.5vw, 1.25rem); margin-top: clamp(1rem, 2.5vw, 1.875rem); }
  .layer { background: #FFF8EE; border: 2px solid #FFE0B2; border-radius: 12px; padding: clamp(1rem, 2vw, 1.5rem); }
  .layer .ln { font-size: 12px; color: #c45500; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; }

  .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: clamp(0.5rem, 1.5vw, 1.125rem); margin-top: clamp(1rem, 2vw, 1.5rem); }
  .stat { background: #232F3E; border-radius: 10px; padding: clamp(1rem, 2vw, 1.625rem) 18px; text-align: center; }
  .stat .num { font-size: clamp(1.5rem, 3.5vw, 2.5rem); color: #FF9900; font-weight: 700; line-height: 1; }
  .stat .label { font-size: 13px; color: #ccc; margin-top: 8px; }

  .quote {
    background: #FFF8EE; border-left: 6px solid #FF9900;
    padding: clamp(1rem, 2vw, 1.5rem) clamp(1.25rem, 2.5vw, 1.875rem);
    margin-top: clamp(1rem, 2vw, 1.5rem);
    border-radius: 0 12px 12px 0;
    font-size: clamp(0.9rem, 1.8vw, 1.375rem); color: #444; line-height: 1.6; font-style: italic;
  }

  .punch-line {
    font-size: clamp(2.5rem, 6vw, 4rem); font-weight: 700; color: #232F3E;
    line-height: 1.2; letter-spacing: -1px;
  }

  /* Responsive: stack grids on narrow viewports */
  @media (max-width: 768px) {
    .layers { grid-template-columns: 1fr; }
    .stats { grid-template-columns: repeat(2, 1fr); }
  }
</style>
</head>
<body>

<div class="progress" id="progress"></div>
<div class="nav-dots" id="navDots"></div>

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

  // Create nav dots
  const dotsContainer = document.getElementById('navDots');
  slides.forEach((_, i) => {
    const dot = document.createElement('button');
    dot.className = 'nav-dot' + (i === 0 ? ' active' : '');
    dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
    dot.addEventListener('click', (e) => { e.stopPropagation(); show(i); });
    dotsContainer.appendChild(dot);
  });
  const dots = dotsContainer.querySelectorAll('.nav-dot');

  function show(i) {
    if (i < 0) i = 0;
    if (i >= total) i = total - 1;
    slides[cur].classList.remove('active');
    slides[i].classList.add('active');
    dots[cur].classList.remove('active');
    dots[i].classList.add('active');
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
    if (e.target.closest('.nav-dots')) return;
    if (e.target.closest('.slide-notes')) return;
    show(cur + 1);
  });
</script>

</body>
</html>
```

---

## Usage Examples

- `#html-ppt Make a Performance Loop intro deck, 10 slides, for PMs and developers`
- `#html-ppt Convert my-talk.pptx to a web slideshow`
- `#html-ppt Quick single-slide poster for the team meeting`
- `#html-ppt Rehearsal deck for my AWS re:Invent talk, 15 slides with speaker notes`
