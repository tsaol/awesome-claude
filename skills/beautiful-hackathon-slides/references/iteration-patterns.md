# Iteration Patterns

Common adjustments users request after seeing the first draft. Each pattern has:
- **User signal** (how they phrase the issue)
- **Root cause**
- **Fix**

Use this as a lookup when user feedback comes in.

---

## Typography Issues

### "Fonts are too small"
**Signal**: "Can't read this on video", "Need larger text for recording"
**Root cause**: Default font sizes optimized for laptop viewing, not video compression
**Fix**:
- Bump body base from `16px` → `clamp(16px, 1.2vw, 20px)` on `body`
- Scale up key headings by adding `clamp()` ranges
- Bump `font-size` on text-heavy elements (quote boxes, card descriptions)
- Usually 15-25% increase across the board works

### "The quote is too dominant / not dominant enough"
**Signal**: "Make the quote bigger/smaller", "This is the pain point, make it pop"
**Root cause**: Quote sizing didn't match its narrative weight
**Fix**:
- Key pain-point quote should be `clamp(1.5rem, 2.4vw, 2rem)` minimum
- Use a distinctive font (italic sans or display serif) for voice effect
- Consider `white-space: nowrap` if it fits — but check it doesn't overflow the container

### "The font for quote looks weird / hard to read"
**Signal**: "Change the font", "Try something else"
**Root cause**: First font choice didn't land
**Fix**:
- Cycle through options appropriate to the active preset. Pick from the preset's typography list in `style-presets.md`, not a generic fallback list.
- For the quote/pain-point element specifically, good contrast options:
  - If body is sans → try a serif italic (DM Serif Display, Instrument Serif, Playfair italic)
  - If body is serif → try the body's italic, or a characterful sans italic (Outfit italic, General Sans italic)
- After changing, ALWAYS update the `@import` URL to include the new font/weights, or you'll get silent fallback (see `style-presets.md` → Font Sanity Check).
- Confirm with the user before committing — they often know it when they see it but can't articulate it

---

## Layout Issues

### "Text is getting cut off / overlapping"
**Signal**: "This text is running into the next section", "Make it fit on one line"
**Root cause**: Column width too narrow OR text too long for container
**Fix** (in priority order):
1. Add `white-space: nowrap;` on the specific element
2. Adjust parent container width (e.g., change 50/50 split to 60/40)
3. Shorten the text content itself
4. Reduce font-size for that element

### "The cards are different heights"
**Signal**: "Make them all the same size", "It looks uneven"
**Root cause**: Card content length varies, flexbox doesn't equalize by default
**Fix**:
- Add `min-height: 90px;` (or appropriate value) to the card class
- In 2x2 grid contexts, CSS Grid already equalizes rows — double-check `display: grid;`

### "Cards in a row should be same width"
**Signal**: "Uneven widths", "They should be identical"
**Root cause**: Flex items sizing to content
**Fix**:
- Add explicit `width` to the card class (e.g., `width: 152px;`)
- Or use `flex: 1` for equal division within a row

### "Horizontal layout feels cramped, vertical would be better"
**Signal**: "Can we stack these?"
**Root cause**: Too much content for horizontal space
**Fix**: Change layout direction
- `flex-direction: column` instead of `row`
- OR use CSS Grid with `grid-template-columns: 1fr` and single column

### "This slide should be split left/right (or vice versa)"
**Signal**: "Make it a split layout" OR "I want this centered, not split"
**Root cause**: Layout doesn't match the content's narrative structure
**Fix**: Completely swap the slide's outer container:
- Split: `flex-direction: row; padding: 0;` with two children that have `width: X%;`
- Centered: `align-items: center; text-align: center; padding: 6vh 8vw;`

---

## Color Issues

### "The colors don't match the theme"
**Signal**: "This should be more [warm/cool/bold/subtle]"
**Root cause**: First color pick didn't resonate
**Fix**:
- Update CSS variables in `:root { }` — typically need to change `--accent-primary`, `--accent-secondary`, and any `-bg` variants
- Keep the *relationships* consistent (border, bg, text should shift together)

### "The pills/tags look weird on white background"
**Signal**: "These look plain", "Give them a colored background"
**Root cause**: Pills using `background: white` or `background: transparent` without visual distinction
**Fix**:
- Add tinted background: `background: var(--accent-bg);`
- Adjust text color to match: `color: var(--accent-deep);`
- Add subtle border: `border: 1.5px solid rgba(accent-rgb, 0.15);`

### "Something is not centered"
**Signal**: "This card should be in the middle", "Looks off to the side"
**Root cause**: Container has `align-items: flex-start` when it should be `center`, OR has extra `padding-top` offset
**Fix**:
- Check the parent flexbox's `align-items` — usually change to `center`
- Remove manual `padding-top` workarounds from earlier drafts
- Verify text-align if appropriate

---

## Content Issues

### "This slide has too much text"
**Signal**: "It's overwhelming", "Can't read this much", "Simplify"
**Root cause**: Paragraph-length descriptions where one-liners would suffice
**Fix**:
- Rewrite each bullet/step to <15 words
- Convert prose to bullet points or tags
- Add visual elements (icons, images, illustrations) to break up text
- Rule: if a slide has more than ~50 words of prose, it's too much for 25 seconds of narration

### "Remove/add a line"
**Signal**: "Delete that part", "I don't need that callout"
**Root cause**: Extra content that doesn't serve the narrative
**Fix**: Just delete. Don't argue to keep it — respect the user's editorial judgment.

### "My team has 5+ members but the grid only shows 4"
**Signal**: "I can't fit my team", "Where do I add more people?"
**Root cause**: Default team-grid pattern assumes 2×2 (4 people)
**Fix**:
- For 5-6 members: switch to 3×2 grid (`grid-template-columns: repeat(3, 1fr);`) and reduce card padding slightly
- For 7-8 members: switch to 4×2 grid with smaller cards
- For 9+ members: consider dropping avatars, using 2 columns of name-only rows, or splitting onto two slides
- Keep member cards identical in size regardless of count — consistency matters visually

### "I don't want this emoji / use a different one"
**Signal**: "That emoji doesn't fit", "Try another one"
**Root cause**: Default emoji didn't match tone
**Fix**: Suggest 3-5 alternatives with different moods. Examples:
- For "thinking": 🤔 💭 🧐 🙇‍♀️
- For "nervous": 😰 😅 🥺 😬
- For "presentation": 📋 💻 🖥️ 📊

---

## Animation Issues

### "The animation is too fast / too slow"
**Signal**: "Wait longer before X appears"
**Root cause**: Animation-delay misaligned with narrative beat
**Fix**:
- Adjust `animation-delay` value
- For mascot/hero entrance: 1.5-2.5s after slide load is typical
- For staggered card reveals: 0.15-0.2s between each

### "The mascot animation blocks text"
**Signal**: "It's covering the button/text", "Move it"
**Root cause**: Absolute-positioned element overlapping content
**Fix**:
- Adjust `bottom` / `right` positioning
- Reduce image size with `width` clamp
- Ensure `z-index` is set properly (image usually above bg, below interactive elements)

---

## Image/Asset Issues

### "The image has a background I don't want"
**Signal**: "Can you remove the white background?"
**Root cause**: Image isn't transparent
**Fix**:
- User needs to use a background remover (e.g., remove.bg, Apple Preview's Remove Background feature)
- Or re-generate the image with transparent background if using AI tools
- Then re-upload and swap the file

### "The image is too small/large"
**Signal**: "Bigger" / "Smaller"
**Root cause**: Default width didn't match visual weight needed
**Fix**:
- Use `clamp(min, preferred, max)` for responsive sizing
- Typical ranges: mascot hero = `clamp(180px, 22vw, 320px)`, sidebar portrait = `clamp(100px, 12vw, 160px)`

---

## Structural Issues

### "This slide should come before/after X"
**Signal**: "Move this earlier/later"
**Root cause**: Narrative flow was off
**Fix**:
- Cut the entire `<div class="slide">` block and paste in new position
- Update all `data-index` attributes on following slides
- Update nav dot count and `goTo()` indices
- Update counter text (`X / Y`)
- If PLAN.md exists, update the slide order there too

### "Add a new slide"
**Signal**: "We're missing a slide about X"
**Root cause**: Original plan was incomplete
**Fix**:
- Add the new `<div class="slide">` with correct `data-index`
- Shift `data-index` of all following slides
- Add new nav dot
- Update counter total
- Update PLAN.md with the new slide
- Update narration-script.md with the new slide's script

### "This whole section is redundant with another slide"
**Signal**: "We already said this on slide X"
**Root cause**: Content duplication from iterative building
**Fix**:
- Remove one of the two slides (usually the later one)
- Reshape the remaining slide to carry the message more completely
- Update indices and PLAN

---

## Browser Refresh Reminders

After every edit:
- Remind the user to refresh the browser (Cmd+R / Ctrl+R)
- If the user opens from Finder, the file might be cached — suggest a hard refresh (Cmd+Shift+R)

---

## When in Doubt

- **Prefer deleting over adding**. Pressure to simplify is always the right instinct.
- **Match the user's vocabulary**. If they say "bigger", the fix is `font-size`, not a layout overhaul.
- **Ship, don't perfect**. After 2-3 iterations on a slide, move on. Hackathon deadlines are real.
