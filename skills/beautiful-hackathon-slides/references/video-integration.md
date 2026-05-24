# Video Integration Guide

Most hackathon decks include live demo recordings (console sessions, web UI walkthroughs, device interactions). This skill reserves explicit placeholder slots for these videos and provides guidance for recording and integration.

Keep this document up to date as new tools emerge or user preferences shift.

---

## Recommended Recording Tools

### macOS Built-in

**QuickTime Player** (free, pre-installed)
- Menu: File → New Screen Recording
- Pros: Zero setup, always available, reliable
- Cons: No zoom effects, basic editing only
- Best for: Simple console/UI recordings where pointing isn't critical

### Third-Party

**OpenScreen** (recommended for hackathon demos)
- https://openscreen.com
- Pros: Smooth zoom in/out during recording, automatic cursor follow, clean export
- Cons: Paid tool (check for free trial during hackathons)
- Best for: Console demos where specific text/clicks need emphasis

**Screen Studio** (strong alternative to OpenScreen)
- https://screen.studio
- Pros: Motion effects, background customization, clean export
- Cons: macOS only, paid
- Best for: Polished demos

**Loom** (free tier available)
- https://loom.com
- Pros: Instant cloud upload, easy sharing
- Cons: Branded watermark on free tier, no zoom effects
- Best for: Informal demos or if sharing is prioritized over polish

### Windows / Linux

- **OBS Studio** (free, cross-platform, powerful but steep learning curve)
- **ShareX** (Windows, free, lots of options)
- **SimpleScreenRecorder** (Linux, lightweight)

---

## Recommended Video Specs

When recording, aim for:

| Spec | Value | Why |
|------|-------|-----|
| Format | MP4 (H.264) | Universal browser support |
| Aspect ratio | 16:9 | Matches `.video-placeholder` |
| Resolution | 1920×1080 minimum | Crisp on modern displays |
| Frame rate | 30fps (60fps OK) | 30 is plenty for screen content |
| Audio | Muted OR clean mic | If with audio, minimize background noise |
| Duration | Match narration script length per slide | 30-60 seconds typical |
| File size | <50MB per clip | Keeps HTML deck loadable |

---

## Recording Workflow

1. **Plan what to show**: Refer to the slide's purpose in PLAN.md. A 30-second demo shows 2-3 key actions, not everything.

2. **Clean up the screen**:
   - Close unrelated apps and browser tabs
   - Hide personal info (emails, usernames where possible)
   - Use a clean desktop wallpaper (or fullscreen the app being demoed)

3. **Practice the flow** (1-2 takes before recording for real):
   - Know what you'll click, type, and when
   - Avoid long silences or hesitation
   - If demonstrating a script, pre-type commands to clipboard

4. **Record**:
   - Start recording, wait 1 second, begin action
   - End with 1 second of hold on the final state (so the end doesn't feel abrupt)

5. **Trim the clip**:
   - Cut dead air at the start/end
   - Final length should match your narration timing

6. **Export as MP4** and save to the `slides/` directory with a clear name like `demo-production-api.mp4`.

---

## Inserting Videos Into the HTML Deck

Once recorded, replace the `<div class="video-placeholder">` block in the HTML deck with a `<video>` tag.

### Autoplay Loop (most common for hackathons)

Video plays automatically when slide is visible, loops until user moves on:

```html
<video src="demo-production-api.mp4"
       autoplay muted loop playsinline
       style="width:72vw;max-width:960px;aspect-ratio:16/9;
              border-radius:16px;box-shadow:var(--shadow-lg);">
</video>
```

**Why `muted`**: Browsers require `muted` for autoplay. If your video has narration baked in, you'll need the `controls` pattern below.

### With Controls (user plays manually)

For videos with audio narration that should play once:

```html
<video src="demo-production-api.mp4"
       controls playsinline
       style="width:72vw;max-width:960px;aspect-ratio:16/9;
              border-radius:16px;">
</video>
```

### Autoplay Once (no loop, no controls)

Plays automatically, stops on last frame:

```html
<video src="demo-production-api.mp4"
       autoplay muted playsinline
       style="...same styling...">
</video>
```

---

## Alternative: Composite in Post-Production

If the user is recording the whole slideshow as one final video (e.g., with OpenScreen capturing the browser window):

1. Keep the `.video-placeholder` divs in the HTML (don't replace them).
2. Record the slideshow play-through with OpenScreen.
3. Record demo videos separately.
4. In video editing software (iMovie, Final Cut, Premiere, DaVinci Resolve), overlay the demo recordings onto the placeholder areas.
5. This approach gives more control over zoom/pan effects on the demo videos.

**When to prefer this approach**:
- User wants animated zoom-ins on specific parts of the demo
- User wants custom transitions between slides and videos
- User is already comfortable with video editing

**When to prefer in-browser video integration**:
- User wants a single HTML deck they can present live
- User prefers to avoid post-production editing
- Simpler workflow, faster iteration

---

## Narration Audio

The AI narration script (`narration-script.md`) can be synthesized separately and overlaid in post-production. Recommended tools:

- **ElevenLabs** — Most natural-sounding, paid ($5-22/mo), best for final production
- **OpenAI TTS** — Solid quality, pay-per-use, voices: `alloy`, `nova`, `onyx`, `echo`
- **PlayHT** — Good conversational tone, subscription
- **Mac system voice** — Built-in, free, but robotic

**Workflow**:
1. Copy each slide's script from `narration-script.md`
2. Paste into chosen TTS tool
3. Generate audio, download as MP3 or WAV
4. In video editor, layer audio over the slide's timeline
5. Adjust slide duration to match audio length

---

## Final Assembly Checklist

Before submitting:

- [ ] All video files are in `slides/` directory, not elsewhere on disk
- [ ] Video paths in HTML use **relative** paths (`demo.mp4`, not `/Users/...`)
- [ ] Narration script has been reviewed for pronunciation edge cases (acronyms, product names)
- [ ] Total runtime matches hackathon requirement (2–5 min typical)
- [ ] File sizes reasonable (<200MB total for the deck + videos)
- [ ] Tested end-to-end playback (opening the HTML, arrow-key through all slides, videos play correctly)
