# Slide Patterns

A catalogue of reusable slide patterns for hackathon decks. Each pattern has:
- **When to use**
- **Structure** (HTML skeleton)
- **Customization notes**

All patterns are style-agnostic — they work across any of the 5 style presets. The styling (fonts, colors) comes from the chosen preset; the layout comes from these patterns.

---

## Core Patterns (include in most decks)

### 1. Title / Hero

**When to use**: Slide 1. Establishes identity, tagline, tech stack, and hackathon badge.

**Structure**:
```html
<div class="slide slide-title active">
  <!-- Optional: brand mark (logo + product name) -->
  <div class="brand-row">
    <div class="brand-hex"></div>  <!-- geometric logo mark -->
    <span class="brand-text">Product<span class="accent">Name</span></span>
  </div>
  <!-- Big tagline -->
  <h1>Your tagline here with <em>emphasized words</em></h1>
  <!-- Subtitle paragraph -->
  <p class="subtitle">One-sentence product description with <span class="hl">highlighted</span> key terms.</p>
  <!-- Tech stack pills -->
  <div class="pill-row">
    <span class="pill">🐝 Service 1</span>
    <span class="pill">🧠 Service 2</span>
    <span class="pill">🔊 Service 3</span>
  </div>
  <!-- Hackathon badge at bottom -->
  <div class="hackathon-pill">🏆 Event Name</div>
  <!-- Optional: animated mascot entering from a corner -->
  <img src="mascot.png" class="mascot-float">
</div>
```

**Customization**:
- Centered OR split layout (both work for title)
- Emphasized word in tagline uses the display serif's italic OR the accent color
- Mascot animation entering from corner after ~1.5-2s delay adds delight

---

### 2. Problem / Pain Point

**When to use**: Slide 2. Establishes emotional resonance before introducing the solution.

**Structure** (split layout, our favorite):
```html
<div class="slide slide-problem">
  <div class="problem-left">  <!-- 55-60% width -->
    <div class="section-label"><span class="line"></span>The Problem</div>
    <h2>Ever walked out of a meeting<br>thinking...</h2>
    <div style="display:flex;gap:24px;align-items:center;">
      <img src="mascot-nervous.png" style="width:140px;">
      <div>
        <div class="problem-quote-box">"Key pain-point quote on one line."</div>
        <p class="problem-subtext">One sentence of elaboration.</p>
      </div>
    </div>
  </div>
  <div class="problem-right">  <!-- 40-45% width, contrasting background -->
    <div class="mascot-scenes">
      <div class="mascot-scene">
        <span class="scene-emoji">😅</span>
        <div>
          <div class="scene-title">Mascot in Scenario A</div>
          <div class="scene-quote">"Something <em>awkward</em> they said…"</div>
        </div>
      </div>
      <!-- 2 more scenes -->
    </div>
  </div>
</div>
```

**Customization**:
- The pain-point quote should be in a distinctive font (not the main body font) to feel "spoken"
- Three scenario cards with matching heights — use `min-height` to normalize
- Emojis should all be faces/emotions for consistency, not mixed with objects
- Left side: cream/base bg. Right side: accent-bg with subtle grid overlay for depth.

**No-mascot variant**: If the project doesn't have a mascot, replace `<img src="mascot-nervous.png">` with either:
- A single large emoji (e.g., `<span style="font-size:clamp(4rem,8vw,7rem);">😰</span>`) sized similarly, OR
- Remove the image slot entirely and make the quote box + subtext take the full left column width.

The three scene cards on the right work fine without a mascot — keep them as persona-driven scenarios.

---

### 3. Solution / Three-Step Pipeline

**When to use**: Slide 3. Communicates the core product in one visual.

**Structure**:
```html
<div class="slide slide-solution">
  <div class="section-label"><span class="line"></span>The Solution</div>
  <h2>Subject verbs. Subject verbs. Subject verbs.</h2>
  <div class="pipeline">
    <div class="pipe-step">
      <div class="pipe-icon" style="border-color: var(--accent-1);">🐝</div>
      <span class="name">Step 1</span>
      <span class="desc">One-line description</span>
    </div>
    <div class="pipe-connector"><svg>→</svg></div>
    <div class="pipe-step">...</div>
    <div class="pipe-connector"><svg>→</svg></div>
    <div class="pipe-step">...</div>
  </div>
</div>
```

**Customization**:
- H2 pattern: "Subject verbs. Subject verbs. Subject verbs." (three short sentences, one per step)
- Each icon gets a different colored border (from secondary palette)
- Arrows use the primary accent color
- Staggered animation: step 1 → arrow → step 2 → arrow → step 3 with delays

---

### 4. Use Case / Narrative

**When to use**: Slide 4. Humanizes the product with a narrative. Choose the framework that best fits the product.

**Narrative frameworks** (pick ONE based on what the product is):

| Framework | When it fits | Example products |
|-----------|--------------|------------------|
| **Day-in-the-life** | Product is used repeatedly throughout a day | Fitness trackers, productivity tools, wellness apps |
| **User journey** | Product has a clear beginning → middle → end flow | Onboarding tools, learning platforms, purchase flows |
| **Before / After** | Product transforms something specific | Refactoring tools, analytics, automation |
| **Scenario** | One specific high-stakes moment where the product shines | Emergency tools, decision-support, niche B2B tools |
| **Persona comparison** | Different user types use the product differently | Multi-sided marketplaces, platforms |

**Structure** (2x2 grid + sidebar — works for all frameworks):

```html
<div class="slide slide-usecase">
  <div class="section-label"><span class="line"></span>Use Case</div>
  <h2>[Character or scenario-specific title]</h2>
  <div class="usecase-content">
    <div class="day-timeline">  <!-- 2x2 grid of 4 narrative beats -->
      <div class="day-step">
        <span class="day-pill step-1">[Beat 1 label]</span>
        <p>One-sentence action or moment.</p>
      </div>
      <div class="day-step"><span class="day-pill step-2">[Beat 2]</span>...</div>
      <div class="day-step"><span class="day-pill step-3">[Beat 3]</span>...</div>
      <div class="day-step"><span class="day-pill step-4">[Beat 4]</span>...</div>
    </div>
    <div class="usecase-sidebar">  <!-- ~280px fixed width -->
      <img src="character-doing-thing.png" style="width:100%;">
      <div class="mascot-name">Character Name (optional)</div>
      <div class="mascot-role">Role (optional)</div>
      <div class="mascot-progress">
        <!-- 3 metric bars with before/after values (optional) -->
      </div>
    </div>
  </div>
</div>
```

**Label examples for each framework**:
- Day-in-the-life: `☀️ Morning`, `💼 At Work`, `🌙 Evening`, `📊 Weekly`
- User journey: `🔍 Discover`, `🛠️ Set Up`, `🚀 Use`, `📈 See Results`
- Before/After: `❌ Before`, `⚡ Trigger`, `✅ After`, `📈 Impact`
- Scenario: `🚨 The Moment`, `🤔 Without`, `✨ With`, `🎯 Outcome`

**Customization**:
- Each step pill uses a different accent color for visual variety
- Text per step: one concise sentence, not paragraph
- Sidebar is optional — skip it for products without a character/persona, make the timeline full-width
- If using a character, sidebar image should show them actively doing the thing (not a generic portrait)
- Progress bars are optional — useful for "before/after" framework, skip otherwise

---

### 5. Flow Diagram (End-to-End Pipeline)

**When to use**: Slide 5. Shows 5-7 step technical pipeline horizontally.

**Structure**:
```html
<div class="slide slide-flow">
  <div class="section-label"><span class="line"></span>How It Works</div>
  <h2>End-to-end pipeline</h2>
  <div class="flow-diagram">
    <div class="flow-box">
      <span class="fb-icon">🐝</span>
      <span class="fb-title">Step Name</span>
      <span class="fb-desc">One-line description</span>
    </div>
    <div class="flow-arrow"><svg>→</svg></div>
    <!-- Repeat for 4-7 total boxes -->
  </div>
  <p class="flow-note">Optional annotation line under the diagram</p>
</div>
```

**Customization**:
- **All flow boxes must have identical width and min-height** — this is visually important
- Middle/important boxes get `highlight-box` class with accent border + accent-bg
- Stagger animations: each box fades up with 0.1s delay from the previous
- Keep box descriptions to ~5-8 words

---

### 6. Architecture Diagram

**When to use**: Slide 6. Technical detail for technical audiences.

**Structure** (vertical flow with horizontal rows):
```html
<div class="slide slide-arch">
  <div class="section-label"><span class="line"></span>Production Architecture</div>
  <h2>Deployed and running in production</h2>
  <p class="arch-subtitle">This is what's actually live — not a mockup.</p>

  <div class="arch-diagram">
    <!-- Row 1: Single entry point -->
    <div class="arch-row">
      <div class="arch-box">📱 Client / Device</div>
    </div>
    <div class="arch-vert-arrow"><svg>↓</svg></div>
    <div class="arch-label">API call label</div>

    <!-- Row 2: Horizontal chain -->
    <div class="arch-row">
      <div class="arch-box cloud-box">🌐 HTTP Gateway</div>
      <svg>→</svg>
      <div class="arch-box cloud-box">⚡ Serverless Function</div>
      <svg>→</svg>
      <div class="arch-box cloud-box">🧠 LLM / AI Service</div>
    </div>
    <div class="arch-vert-arrow"><svg>↓</svg></div>

    <!-- Row 3: Storage + consumer -->
    <div class="arch-row">
      <div class="arch-box cloud-box">💾 Database</div>
      <svg>→</svg>
      <div class="arch-box">🔊 Consumer / Surface</div>
    </div>

    <div style="text-align:center;">
      <span class="arch-deployed-badge">Live in production</span>
    </div>
  </div>
</div>
```

**Customization**:
- Cloud-service boxes use a special class (`cloud-box`) with accent border/bg
- Deployed badge (green dot + text) adds credibility
- Keep labels short: service name + 2-3 words of detail
- Animations cascade in reading order
- Swap service names/icons to match the user's actual stack

**Not every project has a cloud backend.** If the project is local-only, mobile-native, embedded, or otherwise non-cloud, swap the boxes accordingly:

| Project Type | Row 1 | Row 2 | Row 3 |
|--------------|-------|-------|-------|
| **Mobile app (native)** | 📱 iOS/Android client | 🔧 Local state + storage | 🌐 Optional sync API |
| **Desktop app (Electron/native)** | 🖥️ Desktop UI | ⚙️ Application logic | 💾 Local database / files |
| **Browser extension** | 🧩 Extension UI | 🔌 Browser APIs | 🌐 Optional backend |
| **Embedded / IoT device** | 🔌 Device firmware | 📡 Sensor data | ☁️ Optional cloud relay |
| **Local AI tool (runs on user's machine)** | 💻 Local UI | 🧠 On-device model | 💾 Local storage |
| **Static site / no backend** | 🌐 Browser | ⚡ Edge function (optional) | 📦 CDN / static files |

Keep the "this is deployed" badge appropriate to the context — e.g., "Live on TestFlight", "Published on Chrome Web Store", "Running on Raspberry Pi", etc.

---

### 7. Video Placeholder (Live Demo)

**When to use**: Slides 7, 9, 10 (or wherever live demos are inserted).

**Structure**:
```html
<div class="slide slide-demo">
  <div class="section-label"><span class="line"></span>Live Demo</div>
  <h2>What this demo shows</h2>
  <p class="demo-subtitle">One sentence describing what will play.</p>
  <div class="video-placeholder">
    <div class="play-icon"><svg>▶</svg></div>
    <span class="vp-label">Demo Recording Name</span>
    <span class="vp-hint">step 1 → step 2 → step 3</span>
  </div>
</div>
```

**Styling**:
- `aspect-ratio: 16/9` for video area
- Dashed border in accent color to clearly signal "placeholder"
- Play icon as a circle with the accent color background
- Width: 70-75% of viewport, max 960px

**Replacement**: Once user has recorded videos, the `<div class="video-placeholder">` becomes:
```html
<video src="demo-name.mp4" autoplay muted loop playsinline
       style="width:72vw;max-width:960px;aspect-ratio:16/9;border-radius:16px;"></video>
```
See `video-integration.md` for details.

---

### 8. Card Grid (6-Card Feature/Claim Showcase)

**When to use**: When communicating 4-9 discrete points (capabilities, AI uses, differentiators).

**Structure**:
```html
<div class="slide slide-grid">
  <div class="section-label"><span class="line"></span>Section Name</div>
  <h2>One-sentence claim</h2>
  <p class="subtitle">Elaboration sentence.</p>
  <div class="card-grid" style="grid-template-columns: repeat(3, 1fr);">
    <div class="feature-card">
      <span class="ac-icon">📋</span>
      <span class="ac-title">Feature name</span>
      <span class="ac-desc">One line of detail</span>
    </div>
    <!-- Repeat for 5-8 more cards -->
  </div>
  <p class="tagline-italic">Optional italic closing phrase</p>
</div>
```

**Customization**:
- 3×2 grid is most readable (6 cards). 2×3 also works.
- Each card's icon can use a different color from the secondary palette
- Keep card descriptions to 8-15 words

---

### 9. Team + Closing

**When to use**: Last slide. Names the team and ends with tagline.

**Structure**:
```html
<div class="slide slide-team">
  <div class="section-label"><span class="line"></span>Team</div>
  <h2>Team [ProductName]</h2>
  <div class="team-grid">  <!-- 2×2 grid, or 1×4 if small team -->
    <div class="team-member">
      <div class="tm-avatar">👩‍💻</div>
      <span class="tm-name">Name</span>
      <span class="tm-alias">@handle</span>  <!-- optional: GitHub / Twitter / work alias -->
    </div>
    <!-- Repeat for all team members -->
  </div>
  <!-- Brand mark repeated for closure -->
  <div class="team-brand">
    <div class="brand-hex-sm"></div>
    <span class="team-brand-text">Product<span class="accent">Name</span></span>
  </div>
  <p class="team-tagline">Tagline repeated for closure.</p>
  <!-- Optional: vision pills -->
  <div class="vision-row">
    <div class="vision-item">🎯 Future 1</div>
    <div class="vision-item">📈 Future 2</div>
    <div class="vision-item">🌍 Future 3</div>
  </div>
</div>
```

**Customization**:
- Team member role/description is optional — often cleaner without it
- Handles (e.g., `@github-user` or work aliases) help judges contact team members
- Closing tagline ties back to slide 1's tagline

---

## Optional Patterns (use when they fit)

### 10. Composable/Compositional Visual

**When to use**: When explaining a system that "assembles" from parts (like our composable context system).

**Structure**: Multiple columns of "components" connected with `+` and `=` symbols, ending in a "result" card.

```html
<div class="context-visual">
  <div class="ctx-col">
    <span class="ctx-col-label">Column 1</span>
    <div class="ctx-file">item1.md</div>
    <div class="ctx-file">item2.md</div>
  </div>
  <span class="ctx-plus">+</span>
  <div class="ctx-col">...</div>
  <span class="ctx-plus">+</span>
  <div class="ctx-col">...</div>
  <span class="ctx-plus">=</span>
  <div class="ctx-col" style="justify-content:center;">
    <div class="ctx-result">Final Result</div>
  </div>
</div>
```

**Customization**:
- All columns and symbols use `align-items: center` on the parent for vertical alignment
- Auto-detected items get accent color border; user-selected items get secondary accent
- The result card is visually distinct (filled bg, thicker border)

---

### 11. Character / Mascot Hero Card

**When to use**: When the product has a mascot character. Can appear on title, use case, or standalone.

**Structure**:
```html
<div class="mascot-card">
  <img src="mascot.png" class="mascot-emoji" style="width:120px;">
  <div class="mascot-name">Mascot Name</div>
  <div class="mascot-role">Role description</div>
  <div class="mascot-quote">"Something the mascot would say"</div>
</div>
```

**Customization**:
- Card has rounded corners, soft shadow, centered content
- Mascot image should have transparent background
- Quote uses a different font from the rest of the card for "voice" effect

---

### 12. Split with Quote Box

**When to use**: When you want to emphasize a single pain-point quote with visual support.

**Structure**: Already covered in Pattern 2 (Problem slide). The quote box is a rounded rectangle with a colored left border, italic text, distinct font.

---

## Pattern Selection Guide

Based on the user's product and hackathon context, select patterns:

| Context Clue | Suggested Patterns |
|--------------|---------------------|
| Has a mascot/character | Title (centered + animated mascot), Use Case (day-in-life), Problem (scenarios), Team+Closing |
| Technical product | Architecture, Flow Diagram, Composable Visual |
| Multi-component AI system | Composable Visual, Flow Diagram |
| Live device/UI demo | 2-3 Video Placeholders |
| Complex pipeline | Flow Diagram + Architecture (both) |
| Simple 3-part story | Solution Pipeline only |

**Optional "Built with AI" slide**: If the user explicitly wants to highlight their AI development process (e.g., targeting a "Best Use of AI" award), you can add a Card Grid slide showing 4-6 ways AI was used (product design, research, UI generation, narration, etc.). **Otherwise, skip this.** Default focus is on the product, not the meta-process of building it.

---

## Emoji Logo Generation

A lightweight, zero-asset way to give the deck a visual identity: use **emojis as the product logo**. No image files needed, renders everywhere, distinctive, and can carry tone/theme in one glyph.

### When to use emoji logos

Not every style suits this. Use this lookup:

| Style | Emoji logo? | Rationale |
|-------|------------|-----------|
| **Warm Editorial** | ✅ Yes | Place inside a geometric hex/badge for refined feel |
| **Cyber Terminal** | ⚠️ Selective | Only if bracketed as ASCII-style `[🔒]` or paired with mono label |
| **Citrus Punch** | ✅ Yes | Bold, oversized emoji fits the punchy energy |
| **Electric Dusk** | ❌ Avoid | Enterprise premium feel — emojis can feel juvenile here |
| **Pastel Chapters** | ✅ Yes | Storytelling vibe — emoji as "character mascot" is perfect |

### How to pick the right emoji

When generating the logo, consider the hackathon project's theme:

**Step 1**: Identify 2-3 **theme keywords** from the user's project description (Phase 1 answers).
- Example: "sustainable food delivery" → keywords: leaf / earth / delivery / food
- Example: "tool for indie musicians" → keywords: music / guitar / wave / sound
- Example: "fitness tracker for climbers" → keywords: mountain / muscle / stopwatch / rope

**Step 2**: Pick a **primary emoji** that captures the most distinctive keyword.

**Good emoji = specific to the project + has a distinctive silhouette.**
**Cliché emoji = generic "startup-y" aspirations with no semantic tie to the product.**

- ✅ **Good picks** (specific + memorable):
  - Nature/animal/character: 🐝 🦊 🌱 🪴 🔮 🦉 🐢 🦉 🐚 🍄 🦋
  - Specific tools/objects: 📡 🛡️ 🔭 🎙️ 🕹️ 🧪 🧲 🪁 🪩 🧭
  - Food-specific: 🥐 🍵 🌶️ 🍋 🥦 🍯
- ❌ **Avoid these regardless of theme**:
  - 💡 🚀 ⭐ ✨ 💎 ⚡ — startup clichés with no specific meaning
  - 🎯 🎨 🧠 — overused in AI-generated decks. Only pick if DIRECTLY tied to the product (e.g., 🧠 is fine for a neuroscience product; not fine for "improves productivity")
  - 📊 📈 📉 — generic "data" emojis without product specificity

**Step 3**: Optionally pair with a **supporting emoji** for scenes, features, or sub-sections.
- Example primary: 🐝 → scene emojis: 😅 😰 🤔 (same family — faces/expressions)
- Example primary: 🌱 → scene emojis: 🌾 🍃 🌻 (same family — plants)

### Logo display patterns

**Pattern A: Hex badge (best for Warm Editorial, Pastel Chapters)**

```html
<div class="brand-row">
  <div class="brand-hex"></div>
  <span class="brand-text">Product<span class="accent">Name</span></span>
</div>

<style>
.brand-hex {
  width: 56px; height: 56px;
  background: linear-gradient(160deg, var(--accent), var(--accent-deep));
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  display: flex; align-items: center; justify-content: center;
}
.brand-hex::after {
  content: '🐝';  /* <-- replace with the chosen emoji */
  font-size: 26px;
}
</style>
```

**Pattern B: Oversized centered emoji (best for Citrus Punch, Pastel Chapters)**

```html
<div class="hero-emoji">🌱</div>

<style>
.hero-emoji {
  font-size: clamp(3rem, 8vw, 6rem);
  line-height: 1;
  margin-bottom: 1rem;
}
</style>
```

**Pattern C: Bracketed mono label (only option for Cyber Terminal, if used at all)**

```html
<span class="mono-logo">[ 🔒 SENTINEL ]</span>

<style>
.mono-logo {
  font-family: 'Space Mono', monospace;
  color: var(--accent);
  font-size: 1rem;
  letter-spacing: 0.1em;
}
</style>
```

### Prompt template for picking the emoji

When the skill runs, include a prompt like this to Claude:

> Based on the hackathon project described above, pick **one primary emoji** that best captures the product's theme and identity. Also suggest 2-3 **supporting emojis** that could be used for scene cards, feature icons, or category tags throughout the deck. Prefer character-like or iconic emojis over generic startup clichés (avoid 💡🚀⭐). Briefly explain why you picked the primary one.

Then use the chosen emoji in the brand/logo block and carry supporting emojis through the deck for visual consistency.

### Rules to prevent emoji chaos

- **One primary emoji per deck.** Do not rotate the "logo" emoji between slides.
- **2-5 supporting emojis max** across the whole deck. More than that looks like a ransom note.
- **Keep the emoji family consistent.** If the primary is a nature emoji, don't pair with tech-object emojis on scene cards.
- **Hex badges for refined styles, raw emojis for playful styles.** Don't put a hex badge in Citrus Punch — it's too formal for that vibe.

---

## Global Styling Requirements

Regardless of preset, every deck MUST include:

1. **Navigation dots** at the bottom (one per slide, clickable)
2. **Slide counter** ("3 / 12") at the bottom-right
3. **Key hint** ("← → to navigate") at the top-right
4. **Arrow key navigation** (left, right, spacebar)
5. **Click halves** for click-to-navigate (left half = previous, right half = next)
6. **Stagger animations** on slide entry (CSS keyframes with delays)
7. **Consistent section-label pattern**: small uppercase label using the preset's display font with a thin colored line

All of this scaffolding is in `assets/style-preview-template.html`.
