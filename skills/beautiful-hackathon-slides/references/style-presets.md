# 5 Style Presets (Aesthetic Archetypes)

These are **aesthetic directions**, not fixed color schemes. Each direction has:
- A characteristic typography pairing
- A tone/mood
- Guidance for picking colors (but **not hardcoded hex values**)

When generating previews, adapt each preset's color palette to:
1. The user's hackathon theme or existing brand, OR
2. A beautiful, theme-agnostic palette that fits the aesthetic

Do NOT default to the same exact colors every time. Be creative within the archetype.

---

## Preset 1: Warm Editorial

**Aesthetic direction**: Light, serif-driven, magazine-like, refined. Conveys thoughtfulness and craft. Feels like *The New Yorker* redesigned as a product deck.

**Typography** (the signature is the characterful serif — must keep a real serif, not sans):

```css
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;0,9..144,800;1,9..144,300;1,9..144,400&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'Outfit', system-ui, sans-serif;
}
```

Fraunces has distinctive optical sizing and italic variants — essential for this preset.

**Color guidance**:
- Base: warm off-white (cream, ivory, bone, beige)
- Primary accent: one warm pigment that fits the theme (honey, terracotta, ochre, rust, olive, sage, muted coral)
- Secondary accents: 1-2 muted complementary colors for section labels or callouts
- Dark text: almost black, warm-toned (never pure #000)

**When to choose it**:
- Products with emotional / human-centered themes (wellness, communication, education, creativity)
- Teams that want to feel "considered" rather than "move fast and break things"
- Non-technical audiences or mixed audiences

**What makes it distinctive**: Italic display serif for key words. Generous whitespace. Thin colored lines instead of heavy boxes. Section labels in small caps with letter-spacing.

**Avoid**: Bright saturated colors, neon effects, pure white backgrounds, Inter-as-display-font.

---

## Preset 2: Cyber Terminal

**Aesthetic direction**: Dark, mono-driven, hacker-aesthetic, unapologetically technical. Feels like a well-designed developer tool or CLI dashboard. Not edgy-for-its-own-sake — purposeful darkness with precision typography.

**Typography** (the signature is **Syne's distinctive geometric shapes** + **mono accents** everywhere — data, quotes, callouts):

```css
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&family=DM+Sans:wght@300;400;500;700&display=swap');

:root {
  --font-display: 'Syne', system-ui, sans-serif;
  --font-body: 'DM Sans', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Courier New', monospace;
}
```

Syne is chunky and architectural — nothing like other sans-serifs in this skill. JetBrains Mono is iconic for terminal aesthetics.

**Color guidance**:
- Base: near-black, slightly warm or cool (off-black with a 2-5% color shift, not pure #000)
- Primary accent: one saturated neon that fits the theme (electric blue, amber, lime, magenta, cyan)
- Secondary: subtle grid lines, muted grays for secondary text
- Text: warm off-white, never pure white

**When to choose it**:
- DevTools, infrastructure, AI/ML products, security, fintech
- Technical-heavy audiences
- Products that want to feel "hardcore" without being corporate

**What makes it distinctive**: Faint grid backgrounds. Terminal-style `>` prompts for key quotes. Monospace used for data/values. Subtle glow effects on accent elements. Sharp rectangular shapes over soft rounded ones.

**Avoid**: Pastel colors, ornate serifs, purple-on-black clichés, Matrix-style green text.

---

## Preset 3: Citrus Punch

**Aesthetic direction**: Light, bold-sans-driven, punchy, energetic. Feels like a confident startup that's excited about what it's building. Bright without being childish.

**Typography** (the signature is **Bricolage Grotesque's expressive variable widths** — its optical-size axis makes big headlines feel dynamic):

```css
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600;12..96,700;12..96,800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --font-display: 'Bricolage Grotesque', system-ui, sans-serif;
  --font-body: 'Plus Jakarta Sans', system-ui, sans-serif;
}
```

Bricolage has characterful wide headlines that feel energetic. Plus Jakarta Sans pairs cleanly without competing.

**Color guidance**:
- Base: soft off-white or subtle warm tint (not pure white)
- Primary accent: one energetic color that fits the theme (citrus orange, bright yellow, hot pink, electric teal, vibrant green)
- Secondary: 2-3 supporting colors for categorization (used sparingly for chips/tags)
- Dark text: strong contrast, near-black

**When to choose it**:
- B2C products, social products, creative tools, media, gaming
- Younger audiences or mainstream appeal
- Products with a "fun but professional" personality

**What makes it distinctive**: Large bold headlines. Color-coded category chips (pill-shaped). Colored underline/highlight effects behind key words. Strong geometric shapes. High information density in cards.

**Avoid**: Gradient overload, emojis everywhere, cartoon-y illustrations, overly saturated backgrounds.

---

## Preset 4: Electric Dusk

**Aesthetic direction**: Dark, clean-sans-driven, sleek, professional. Feels premium and considered — like an enterprise SaaS that hired a designer who actually knew what they were doing.

**Typography** (the signature is **Manrope's refined neutrality with a hint of warmth** — single family, weight variation for hierarchy):

```css
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap');

:root {
  --font-display: 'Manrope', system-ui, sans-serif;
  --font-body: 'Manrope', system-ui, sans-serif;
}
```

Manrope is tighter and more refined than the other sans choices — feels premium without being cold. Display uses weight 700-800, body uses 400.

**Color guidance**:
- Base: deep navy, charcoal, or rich dark tone (not black — slight color temperature)
- Primary accent: one elegant bright color (electric violet, ice blue, warm amber, emerald)
- Secondary: soft muted tones for supporting elements, gradients for atmosphere
- Text: soft warm white with hierarchy tiers (100%, 70%, 50% opacity)

**When to choose it**:
- B2B enterprise tools, fintech, data platforms, infrastructure
- Judges who are executives or senior engineers
- Products that need to project "seriousness" but with design quality

**What makes it distinctive**: Subtle gradient meshes in backgrounds. Fine-line borders instead of heavy boxes. Thoughtful hierarchy with opacity. Mathematical / architectural compositions. Never feels "plain dark" — always atmospheric.

**Avoid**: Neon glow effects, mono fonts (too techy), bright saturated accents, sci-fi aesthetics.

---

## Preset 5: Pastel Chapters

**Aesthetic direction**: Light, soft-duotone, split-panel, storytelling-focused. Every slide feels like a two-page spread in a design magazine or illustrated book — one pastel color on the left, a different pastel on the right, with each slide reading as its own "chapter."

**Typography** (the signature is **Nunito's rounded, friendly character** — single family, weight variation, storybook-like warmth):

```css
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800;900&display=swap');

:root {
  --font-display: 'Nunito', system-ui, sans-serif;
  --font-body: 'Nunito', system-ui, sans-serif;
}
```

Nunito's rounded terminals make it feel human and approachable — visibly different from every other preset's fonts. Display uses weight 800-900, body uses weight 400.

**Color guidance**:
- Pick **two complementary pastel background colors** that work together (e.g., peach + lavender, mint + blush, butter + sky, sage + salmon, lilac + cream)
- These two backgrounds **alternate per slide**, OR split on each slide (left half one color, right half the other)
- One **muted accent color** serves as the "brand" tone — used for key words in headings, section labels, and primary highlights. Pick something grounded: muted purple, terracotta, deep teal, warm coral, olive, dusty rose
- A **palette of 4-6 candy-colored "pill" tags** for categorization (mint, yellow, pink, blue, orange, lilac) — used to label sections, timelines, or categories. They're playful but controlled
- Text: warm dark, never pure black

**When to choose it**:
- Education, wellness, creativity tools, consumer products
- Projects with strong character/mascot narratives or day-in-the-life stories
- Pitches that emphasize empathy, storytelling, or emotional resonance
- Teams that want to feel "designed" and "considered" without being too corporate

**What makes it distinctive**:
- **Split-panel layout** on most slides — the two pastel backgrounds divide each slide into left and right "pages"
- Optional subtle grid overlay on one of the panels for depth (e.g., 40px × 40px lines at very low opacity)
- **Floating white cards** with soft shadows sit on the pastel panels — containing content like quotes, metrics, or callouts
- **Slide numbers** displayed in the corner (e.g., `01`, `02`) in the accent color — reinforces the "chapter" feel
- **Bold headings where one word uses the accent color** (e.g., "Product**Name**" or "The **Solution**")
- **Color-coded pill badges** for inline categorization — a signature element

**Avoid**:
- Saccharine color combinations (baby pink + baby blue feels juvenile)
- Mixing serif + sans + mono (this style commits to one sans family)
- Comic sans or overly rounded display fonts
- Too-high saturation pastels (the colors should feel muted/dusty, not neon)
- Hand-drawn illustrations (clean vector or emoji characters fit better)

**Flexibility note**: The signature is the *split-panel + duotone + single-sans* combination. The specific colors, accent hue, and font choice should adapt to the user's project theme. Don't default to peach+lavender+purple every time — that's just one example. A wellness app might use mint+cream+sage. A food startup might use butter+blush+terracotta.

---

## Critical: Font Weight Matters

**A common failure mode**: the deck looks thin, weak, and generic because imported font weights are too light, or because the `@import` URL doesn't match the `font-family` names used in CSS, causing silent fallback to system fonts.

**Rules to prevent this**:

1. **Always import multiple weights**. A display font needs **400 (body), 500, 600, 700, and 800** to render hierarchy correctly. For `h1`/`h2`, default to **weight 800** — thinner display text looks weak on slides.

2. **Import italic variants** if the preset uses italic for emphasis (e.g., Warm Editorial italicizes key words in headings).

3. **The font name in `font-family` MUST match the font in the `@import` URL.** Writing `font-family: 'Bricolage Grotesque'` when only `Fraunces` was imported causes silent fallback to system fonts → thin, ugly result.

4. **Use CSS variables `--font-display` and `--font-body`** (from the template) — never hardcode `font-family: 'Outfit'` in component CSS, or the fonts won't swap when the preset changes.

---

## Font Distinctiveness Summary

All 5 presets use **completely different primary display fonts**, so every preview should look visibly distinct:

| Preset | Primary Font | Signature Visual Feel |
|--------|--------------|-----------------------|
| Warm Editorial | **Fraunces** (serif) | Classic magazine elegance |
| Cyber Terminal | **Syne** + **JetBrains Mono** | Chunky geometric + terminal code |
| Citrus Punch | **Bricolage Grotesque** | Expressive optical-size bold |
| Electric Dusk | **Manrope** | Refined premium neutrality |
| Pastel Chapters | **Nunito** | Rounded friendly warmth |

If two preview files use the same primary display font, one of them is wrong. All 5 fonts above must be different — that's what makes "Show Don't Tell" actually work.

---

## Non-English / Multi-Language Slides

If the deck is in a language other than English (Chinese, Japanese, Korean, Arabic, Cyrillic, Hindi, etc.), most of the fonts suggested in Ready-to-paste Font Blocks **will NOT render the characters correctly** — they'll fall back to system fonts, breaking the visual consistency.

### What to use instead

For **Chinese (Simplified / Traditional)**:
- Display + body: `Noto Sans SC` or `Noto Serif SC` (or TC for Traditional) — import from Google Fonts
- Pair with a Latin font for any English text mixed in (e.g., `Noto Sans SC + Outfit`)

For **Japanese**: `Noto Sans JP` / `Noto Serif JP`

For **Korean**: `Noto Sans KR` / `Noto Serif KR`

For **Arabic**: `Noto Sans Arabic` / `Noto Kufi Arabic`

For **Cyrillic / Hindi / Thai / Hebrew**: corresponding `Noto Sans ...` family

### How to adapt presets

The aesthetic direction still applies — only the specific font changes:

- **Warm Editorial in Chinese**: `Noto Serif SC` (for display) + `Noto Sans SC` (for body)
- **Cyber Terminal in Japanese**: `Noto Sans JP` + mono (`M PLUS 1 Code` has a CJK-aware mono feel)
- **Citrus Punch in Korean**: `Noto Sans KR` with heavy weights (700/800)
- **Electric Dusk in Chinese**: `Noto Sans SC` — single family with weight variation
- **Pastel Chapters in Japanese**: `Noto Sans JP` — single family with weight variation

The color palettes, layout patterns, and sizing all stay the same. Only `@import` URL and `font-family` change.

---

## Font Sanity Check (run after generating)

After generating any preview or deck, verify:

- [ ] The `@import` URL loads successfully (open HTML in browser, check Network tab — no failed requests)
- [ ] Every font name in `font-family` declarations appears somewhere in the `@import` URL
- [ ] Display font weight 700 or 800 is imported (otherwise `h1`/`h2` will look thin)
- [ ] If using italics anywhere (Warm Editorial), italic variants are imported (`ital@1`)
- [ ] When viewed in browser, `h1`/`h2` look **bold and designed**, not thin/generic

### For Phase 2 specifically (5 previews)

Additional distinctiveness check:
- [ ] Open all 5 previews side-by-side
- [ ] **Each preview should use a visibly different primary display font** — Fraunces / Syne / Bricolage / Manrope / Nunito
- [ ] If two previews look like "the same font with different colors", one of them has the wrong font. Fix before showing the user.
- [ ] The **quickest way to check**: look at the big h1 on each title slide. They should look like 5 different typefaces, not 5 variants of one.

If any of these fail, the fonts won't render correctly and the output will look amateurish regardless of layout/color choices.

---

## Color Priority: User Preference vs. Context vs. Archetype

**A subtle but critical rule**: when the user states a color preference ("I like pink", "make it green"), do NOT apply it to all 5 previews. Users don't know what they want until they see it — this is the whole point of Phase 2 (Show Don't Tell).

### Priority order (high to low)

1. **Preset archetype** — The 5 presets are by definition 5 different aesthetic directions. Each has its own natural color vocabulary. Never violate this. Electric Dusk doesn't do neon pink; Cyber Terminal doesn't do pastel mint. Honor the archetype first.

2. **Negative preferences** ("I hate X") — Respect 100%. Users are usually well-tested on what they dislike. Zero previews should violate a negative preference.

3. **Theme context** (inherent to the product) — Sustainability products lean green. Medical/health leans blue or white. Food leans warm. This is objective information about the product, not the user's taste. Weight this moderately.

4. **Positive preferences** ("I like pink") — Weak signal. Respect it in **some but not all** previews. Typically 2-3 out of 5 should honor a stated positive preference; the remaining 2-3 should deliberately explore other directions.

5. **Variety and contrast** — The 5 previews together must cover genuinely different palettes. If all 5 look similar, you've failed Show Don't Tell, regardless of how well you honored preferences.

### Practical rule for 5 previews

Given a user who says "I like pink":

| Preview | Treatment | Why |
|---------|-----------|-----|
| 1 | Honors preference where preset supports it | Shows "you can have what you want" |
| 2 | Honors preference where preset supports it | Same — another expression of the preference |
| 3 | Theme-driven palette, ignores preference | Shows "the product theme suggests other colors" |
| 4 | Deliberate contrast — no pink at all | Shows "here's a direction you didn't ask for" |
| 5 | Design-intuition palette, beautiful but unrelated | Sometimes the best option comes from nowhere |

**Result**: 2 previews honor the preference, 3 deliberately explore alternatives. The user gets to compare their initial instinct against options they didn't request — and often discovers they prefer one of those.

### Why this matters

- Users often can't articulate design preferences accurately. "I like pink" might mean "I want something warm and soft" — which could be better served by cream+terracotta than by actual pink.
- The moment of design insight is *"oh, I didn't know I'd like this"*. That can't happen if all 5 options conform to stated preferences.
- Generating 5 variations of the stated preference is the same failure mode as generating generic AI slop — it privileges the user's first instinct over showing them the possibility space.

### What to avoid

- **Don't** generate 5 pink previews because the user said "pink".
- **Don't** ignore positive preferences entirely — that feels disrespectful.
- **Don't** force a color into a preset where it doesn't fit (pink in Electric Dusk looks tacky; preserve archetype integrity).
- **Don't** hedge with "slightly pink-tinged" variations across all 5 — commit fully to preference in some, fully contrast in others.

### Impression choice and preset fit

The user's "first impression" answer from Phase 1 can also nudge which presets feel most natural (though all 5 are still generated):

| Impression | Most natural presets | Why |
|------------|---------------------|-----|
| Technically impressive | Cyber Terminal, Electric Dusk | Technical aesthetics signal depth |
| Beautifully designed | Warm Editorial, Pastel Chapters | Design-forward aesthetics signal craft |
| Solves a real problem | Warm Editorial, Pastel Chapters | Warm, human-centered aesthetics signal empathy |
| Creative / Bold | Citrus Punch, Pastel Chapters | Energetic/unconventional aesthetics signal creativity |

This does NOT restrict the previews — all 5 are always shown. But if the user is torn between two presets in Phase 2, this mapping can help you recommend one.

### When explaining to the user

After generating the 5 previews, be transparent:
> "I generated 2 options that lean into your preference for [color], and 3 that deliberately explore other directions — often people discover they prefer something they didn't ask for. Take a look at all 5 before deciding."

This sets the right expectation and invites the user to update their own preferences based on visual evidence.

---

## Preview Summary Table (for showing the user)

When presenting 5 previews, use this summary:

| Option | Preset               | Feel                              |
|--------|---------------------|-----------------------------------|
| 1      | Warm Editorial      | Light, serif, refined, magazine   |
| 2      | Cyber Terminal      | Dark, mono, hacker-precise        |
| 3      | Citrus Punch        | Light, bold sans, energetic       |
| 4      | Electric Dusk       | Dark, clean sans, premium B2B     |
| 5      | Pastel Chapters     | Light, split-duotone, storytelling |

*(Step-by-step preview generation instructions live in `workflow-phases.md` Phase 2. This file is the source of truth for WHAT each preset is; the workflow file is the source of truth for HOW to generate previews.)*

---

## Rule: No Style Should Feel "Safe"

If all 5 previews feel like variations on the same idea, you've failed the Show-Don't-Tell principle. Each preset should make the user think "oh wow, that's a different vibe." Bold commitment to each direction beats hedging.
