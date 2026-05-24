# Workflow Phases

This skill follows 9 phases (0 through 8). Each has clear inputs, outputs, and exit criteria. Do not skip phases — they exist to prevent the generic-AI-slop failure mode.

---

## Phase 0 — Discover

**Goal**: Understand what the user is trying to accomplish.

**Input**: User's initial message (often vague: "help me make hackathon slides").

**Action**:
- Read any linked context files (project docs, pitch descriptions, hackathon rules).
- Note: do NOT start designing yet. This phase is pure listening.

**Output**: Mental model of the project and its scope.

**Exit criteria**: You can summarize the project in one sentence.

---

## Phase 1 — Clarify

**Goal**: Gather the minimum context required to generate Phase 2 previews.

**Guiding principle**: Only ask questions that block Phase 2. Everything else is deferred to the phase where it actually matters. Prefer user-provided documents over granular questions — if they can share a project description, README, or pitch doc, that replaces half the questions.

### Step 1: Ask for existing context (if not already shared)

Open with:
> "Before I ask anything, do you have an existing project description, README, pitch doc, or idea file I can read? Even a paragraph of notes helps — I'll extract what I need from it."

If yes: read it thoroughly and derive answers to the blocker questions below. Only ask what's still missing.

If no: proceed to Step 2 and ask for the minimum.

### Step 2: Blocker questions (ask only what's missing from Step 1)

These are the ONLY things needed to generate Phase 2 previews. Ask all 5 together in one message. Each question is a natural-language prompt with an example to guide the user's answer format.

> **Q1**: What hackathon is this for, and how long is the demo video?
> *(e.g., "HackTheNorth 2024, 3-minute video limit")*
>
> **Q2**: What's your product called, and who does it help do what?
> *(e.g., "FitClimb — helps climbers track their training progress and route difficulty")*
>
> **Q3**: Who will be watching — mostly technical people, non-technical, or a mix?
> *(e.g., "technical judges from the engineering org" or "mixed — some engineers, some PMs")*
>
> **Q4**: Do you already have any brand colors, a logo, or a mascot? If not, no worries — I'll design from scratch.
> *(e.g., "we have a green leaf logo" or "nothing yet")*
>
> **Q5**: After watching your demo, what do you most want judges to walk away thinking?
> *(e.g., "these people are technically strong" or "this really solves a pain point" or "wow that design is clean")*

**How to use the answers**:
- Q1: Time limit determines narration word budget in Phase 6.
- Q2: Product name and description populate preview content so slides show real text, not placeholders. If the user struggles with this, help them — rephrase what they said into a one-liner and confirm.
- Q3: Audience level decides whether to include an architecture slide and how much technical depth to show.
- Q4: Existing visual identity informs color choices in Phase 2 previews. No identity = full creative freedom.
- Q5: The "impression" answer does NOT affect which style previews are shown (Phase 2 always shows all 5 presets). It affects Phase 3 — which slides get detailed treatment and which get simplified. Map the user's free-text answer to the closest category: technically impressive / beautifully designed / solves a real problem / creative and bold.

### Explicitly defer these to later phases (do NOT ask now)

| Question | Deferred to |
|----------|-------------|
| Team member names, roles, aliases | Phase 3 (when building the Team slide) or Phase 5 (iteration) |
| Narrator type (human / AI / mixed) | Phase 6 (when generating script) |
| Recording / editing tool | Phase 7 (when integrating videos) |
| Detailed tech stack breakdown | Phase 3 (when building Architecture slide) — or pulled from Step 1 doc |
| Problem / solution detail sentences | Phase 3 (pulled from Step 1 doc, or asked per-slide if needed) |
| Awards / categories targeted | Not asked — doesn't affect HTML output. Focus on product, not meta-awards. |

### Anti-patterns to avoid

- **Don't ask "what style do you want?"** — users can't answer this well. Save it for Phase 2 visual previews.
- **Don't ask about colors in words**. Save that for visual previews.
- **Don't ask about fonts**. Same reason.
- **Don't ask granular product questions** ("what does your product do? what's the tech stack?") if the user already shared a doc. Read the doc.
- **Don't pepper the user with 10+ questions**. If Step 1 covers most of it, Step 2 might be only 1-2 follow-ups.

### Note on stated preferences

If the user volunteers a color preference ("I want it pink!"), capture it but treat it as a **hypothesis, not a requirement**. In Phase 2 you'll honor it in some previews and contrast with it in others — users often discover they prefer something they didn't ask for. See `references/style-presets.md` → "Color Priority" for the weighting rules.

**Output**: Enough context to start Phase 2 — product name, one-liner, audience, time limit, any existing visual identity.

**Exit criteria**: You have answers (or confident inferences from the provided doc) for all 4 blocker questions. Restate your understanding back to the user briefly for confirmation — but don't belabor it.

---

## Phase 2 — Preview (Show, Don't Tell)

**Goal**: Let the user pick an aesthetic direction from visual options.

**Action**:
1. Load `references/style-presets.md` and `references/slide-patterns.md` (the latter for the Emoji Logo Generation section).
2. **Review the "Color Priority" section** in `style-presets.md`. If the user stated any color preferences in Phase 1, plan to honor them in only 2-3 previews and deliberately explore alternatives in the other 2-3. Users don't know what they want until they see it — never generate 5 variations of the same stated preference.
3. **Pick an emoji logo** that fits the project theme (see `slide-patterns.md` → "Emoji Logo Generation" for how to choose). Use this emoji consistently across all 5 previews so the user evaluates styles, not logos.
4. Generate 5 HTML preview files, each containing 3 sample slides:
   - **Sample Slide 1**: Title / hero — showcases typography, layout, and tone. Include the emoji logo (in the style-appropriate pattern — hex badge, oversized, bracketed mono, etc.).
   - **Sample Slide 2**: Content slide — the "Problem" or a similar content-rich slide.
   - **Sample Slide 3**: Live demo placeholder — shows how video insertion will look.
5. **For each preview, apply the preset's exact font block** — the `@import` URL and `:root { --font-* }` CSS variables are **inline in each preset's description** in `style-presets.md`. Copy-paste these verbatim. Do NOT leave the template's default Fraunces+Outfit — that will cause all 5 previews to look identical (the #1 failure mode of this skill).

   **Distinctiveness requirement**: The 5 previews must use 5 different primary display fonts: Fraunces (Warm Editorial), Syne (Cyber Terminal), Bricolage Grotesque (Citrus Punch), Manrope (Electric Dusk), Nunito (Pastel Chapters). If two previews end up with the same primary font, one of them was built wrong.
6. Use the user's Phase 1 answers to inform each preview's content (e.g., actual product name, real problem statement).
7. Name files `preview-option-1.html` through `preview-option-5.html`.
8. **Run Font Sanity Check on each preview** before opening (see `style-presets.md`). Each preview's `@import` must match its `font-family` declarations, or the preview will show generic system fonts and fail the "show don't tell" purpose.
9. Open all 5 in the browser simultaneously so the user can compare.
10. **When presenting to the user, be transparent about color choices**: if you honored their stated preference in some previews and deliberately contrasted in others, say so. Example: "2 of these lean into your preference for [color], 3 deliberately explore other directions."
11. Ask the user which one resonates. Accept mixed feedback ("I like 2 but prefer 4's layout") and offer to combine.

**Critical**: The 5 previews must be **genuinely different** — not safe variations. Cover light/dark, serif/sans/mono, warm/cool, minimal/maximal. Refer to `references/style-presets.md` for the 5 aesthetic directions.

**Escape hatch: if the user rejects all 5**:
- Do NOT generate 5 new previews from scratch — that's wasteful.
- Ask specific, diagnostic questions: "What specifically didn't work — the colors? The layout density? The overall feeling? Too bold or too subtle?"
- Based on answers, generate **2-3 targeted new previews** that address the rejection (e.g., if they said "too cold", generate warmer takes on the presets that lean cool).
- Combine elements from previously-liked-but-imperfect options: "You liked #2's typography but #4's color palette — here's a hybrid."
- If the user still can't decide after the second round, present the 2-3 strongest options and recommend one with reasoning.

**Output**: 5 preview HTML files + user's chosen direction.

**Exit criteria**: User picks a direction (possibly with modifications), or accepts a recommendation from the escape-hatch round.

---

## Phase 3 — Build

**Goal**: Generate the full deck in the chosen style.

**Action**:
1. Delete the 4 non-chosen preview files (clean up the workspace).
2. Load `references/slide-patterns.md` and `references/style-presets.md`.
3. **Apply the chosen preset's fonts**: the exact `@import` URL and `:root { --font-* }` CSS block is inline in each preset's description in `style-presets.md`. Copy-paste verbatim into the scaffolding. Do NOT retype from memory (URL typos cause silent font-load failures), and do NOT leave the template's Fraunces+Outfit defaults unless the chosen preset is Warm Editorial.
4. **Pick an emoji logo** (if the chosen style supports it — see "Emoji Logo Generation" in `slide-patterns.md`). Select one primary emoji that captures the project theme, and 2-3 supporting emojis for scene cards / feature icons. Avoid startup clichés (💡🚀⭐).
5. **Ask for team info now** (deferred from Phase 1): "I'm about to add the Team slide — what are the team members' names? Any handles, aliases, or roles to include?" Keep this brief.
6. **Ask about live demo recordings** (deferred from Phase 1): "Will there be live demo recordings inserted? If yes, what's being shown (console, web UI, device, animation)? I'll leave placeholder slots for them." This decides how many `video-placeholder` slides to include.
7. **Apply the user's Impression choice** from Phase 1 to decide slide emphasis:

   | Impression | Emphasize (more detail, more time) | Simplify (lighter treatment) |
   |------------|-------------------------------------|-------------------------------|
   | Technically impressive | Architecture diagram, Flow diagram, technical pipeline | Problem/empathy slide |
   | Beautifully designed | Title animation, Use Case visuals, typography/spacing precision | Architecture detail |
   | Solves a real problem | Problem slide (core focus), Use Case narrative, mascot/character | Technical pipeline depth |
   | Creative / Bold | Unconventional layouts, strong animations, bold color usage | Traditional architecture format |

   These are guidelines, not hard rules. Blend based on the user's project context.

8. Build a single-file HTML deck (`<project-name>-deck.html`) with:
   - Core patterns: title, problem/content, solution, use-case, architecture, video-placeholder, team-closing
   - Optional patterns based on the project: composable visual, day-in-life timeline, flow diagram, etc.
9. Use the base scaffolding from `assets/style-preview-template.html` for navigation, animations, and viewport handling.
10. In per-component CSS, use `var(--font-display)` / `var(--font-body)` — never hardcode font names like `font-family: 'Fraunces'`, or fonts won't swap when the preset changes.
11. Aim for **10–14 slides** total. Default: 12.
12. **Run the Font Sanity Check** from `style-presets.md` before handing off to the user. Verify: @import URL matches font-family declarations, weight 700+ is imported, italic variants are imported if used.
12. Open the deck in the browser so the user can review.

**Output**: A complete HTML deck.

**Exit criteria**: User has seen the deck and isn't blocked from providing feedback.

---

## Phase 4 — Document (Optional but Recommended)

**Goal**: Persist context in a PLAN.md so future iterations stay aligned.

**Action**:
1. Offer to generate `PLAN.md` using `assets/plan-template.md`.
2. Populate with:
   - Hackathon context from Phase 1
   - Chosen style direction from Phase 2
   - Slide-by-slide breakdown with timing
   - Video insertion points
   - Team info
3. If the user declines, skip this phase — but note that iteration in Phase 5 will be harder.

**Output**: `PLAN.md` (if accepted).

**Exit criteria**: PLAN.md exists OR user explicitly declined.

---

## Phase 5 — Iterate

**Goal**: Refine specific slides based on user feedback.

**Action**:
1. Load `references/iteration-patterns.md`.
2. Apply common adjustment patterns:
   - "Font too small" → bump font-size values
   - "Text overlapping with next column" → add `white-space: nowrap` or split columns
   - "Colors feel off" → update CSS variables
   - "This slide has too much text" → rewrite with shorter phrasing + visuals
3. After each edit, remind the user to refresh the browser.
4. **Update PLAN.md on "significant changes"**. Significant = any of these:
   - Slide added, removed, or reordered
   - Style preset pivoted to a different one
   - Target video length changed (e.g., 3min → 5min)
   - Major content restructure (new narrative arc, different pitch framing)
   - Team members added/removed
   Non-significant (skip the update): font-size tweaks, color-variable adjustments, emoji swaps, copy polish on one slide.
5. **If the user iterates on the same slide 3+ times**, gently suggest moving on: "This slide is in a good place — want to move to the next one or start on the narration script? Hackathon deadlines are real."

**If iterations change slides AFTER Phase 6 has run** (scripts already generated):
- For each added/removed/reordered slide, mark the corresponding script section as stale
- Re-generate only the affected sections, not the whole script
- Update the runtime estimate table at the bottom of `narration-script.md`

**Output**: Refined deck.

**Exit criteria**: User says "I'm satisfied", OR after 2-3 rounds of polish on the same element you've offered to move on and they agree.

---

## Phase 6 — Narrate

**Goal**: Generate an AI narration script matched to the target video length.

**Action**:
1. **Ask about the narrator** (deferred from Phase 1): "Will you use an AI voice (ElevenLabs, OpenAI TTS, etc.), record your own voiceover, or mix both?" This affects the tone of the script (AI voice works best with shorter, punchier sentences; human narration can handle more nuance).
2. Load `assets/narration-script-template.md`.
3. For each slide, write a 1-4 sentence script.
4. Budget total words: roughly **170 words per minute** of AI TTS.
   - 2-minute video → ~340 words total
   - 3-minute video → ~510 words total
   - 4-minute video → ~680 words total
   - 5-minute video → ~850 words total
5. Include:
   - Per-slide word count estimate
   - Total runtime estimate table
   - Recommended AI voice tools (ElevenLabs, OpenAI TTS, PlayHT)
   - Recording notes (tone, pace, emphasis words, pause markers)
6. Keep the tone **conversational, confident, not corporate**. Think "smart friend explaining a cool project," not "enterprise training video."

**Output**: `narration-script.md`.

**Exit criteria**: User accepts the script or requests edits.

---

## Phase 7 — Integrate (Video Insertion)

**Goal**: Guide the user through replacing video placeholders with real recorded demos.

**Action**:
1. **Ask about recording tools** (deferred from Phase 1): "What are you using to record the demo videos? And what will you use to assemble the final video — OpenScreen, iMovie, Final Cut, Premiere, DaVinci Resolve, or something else?" This determines whether to replace placeholders with inline `<video>` tags or keep placeholders for post-production compositing.
2. Load `references/video-integration.md`.
3. Walk through:
   - Recording with recommended tools (QuickTime Player, OpenScreen, Loom)
   - Recommended video specs (MP4, 16:9, 1080p+, H.264)
   - How to replace `<div class="video-placeholder">` with `<video>` tag in the HTML
   - Autoplay / loop / controls decisions
4. If the user is using OpenScreen or similar tools for final assembly, recommend keeping the placeholders and compositing in post-production — gives more control over zoom/pan effects.

**Output**: Deck with real videos OR clear instructions for when the user has recordings.

**Exit criteria**: User has what they need to finish the demo video.

---

## Phase 8 — Submit

**Goal**: Package the final deliverables according to the hackathon's submission requirements.

**Action**:
1. Ask what the submission format is (if not already captured in Phase 1):
   - **Video file only** (most common) — export final MP4, check length against time limit
   - **Video upload URL** (YouTube, Vimeo, S3, internal platform) — user uploads, shares link
   - **Video + written description** — make sure user has prepared the description (often markdown-supported, 1-3 paragraphs)
   - **Source code archive** (.zip of the project) — separate from the demo video
   - **Deployed URL** (for live-demo-able projects)

2. Final deck checklist before submission:
   - [ ] Video plays end-to-end in a fresh browser / fresh player (no cached assets)
   - [ ] Total runtime is within the hackathon's stated range
   - [ ] No placeholder text like `<Project Name>` or `<REPLACE THIS>` leaked into the final output
   - [ ] No project-specific private information accidentally visible (API keys in recordings, internal URLs, personal emails)
   - [ ] Audio plays correctly (AI narration audible, no clipping)
   - [ ] File name is descriptive (e.g., `<project-name>-demo-<year>.mp4`, not `final_final_v3.mp4`)

3. If the hackathon requires a **written description** to accompany the video:
   - Help the user adapt the narration script into a 1-2 paragraph description
   - Include: problem, solution, what's unique, tech stack, team
   - Keep it scannable — judges read fast

4. If source code is submitted separately:
   - Help user prepare a clean README for their project repo (not this slides repo)
   - Suggest a `.gitignore` that excludes: `*.mp4` (large video files), personal credentials, `node_modules/`

**Output**: Submission-ready artifacts.

**Exit criteria**: User has uploaded/submitted successfully, OR has everything they need to do so.

---

## Phase Dependencies

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8
                       ↑          ↑         ↑         ↑         ↑
                       └──────────┴─────────┴─────────┴─────────┘
                       (Phase 5 can trigger return to earlier phases if rework is needed)
```

**Non-linear paths**:
- Phase 5 → Phase 2: User decides the style was wrong after building the deck. Use the Phase 2 escape hatch (2-3 targeted previews, not 5 new ones).
- Phase 5 → Phase 6: Scripts become stale when slides change after narration is generated — update only affected sections.
- Phase 4 → Phase 6: User wants the script before iterating more. Acceptable; PLAN.md can be populated later.

**What NOT to do**:
- Phase 0 → Phase 3: Skipping Phase 1 and 2 guarantees generic output.
- Phase 6 before Phase 5: Writing the script before iterating on slides wastes effort when slides change.
- Phase 8 without testing: Never submit without playing the final video end-to-end in a fresh browser session.
