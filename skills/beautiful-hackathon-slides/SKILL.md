---
name: beautiful-hackathon-slides
description: Create distinctive, production-grade hackathon demo decks with bold design choices that stand out from typical technical presentations. Use when building pitch decks for hackathons, demo days, or competition submissions that need to combine technical depth with visual polish.
---

# Beautiful Hackathon Slides

A Claude Code skill for building **hackathon pitch decks that stand out** — not the typical black-console-screenshot technical demo, but a visually distinctive, startup-pitch-style presentation that makes judges take notice.

## When to Use

Trigger this skill when the user asks to:

- Create slides / a deck / a pitch / a presentation for a hackathon
- Build a demo video that includes slides as the visual background
- Design a submission for an MLH hackathon, university hackathon, company hackathon, or similar competition
- Make a pitch deck for demo day, startup competition, or product showcase

Do NOT use for:

- Corporate training slides or enterprise presentations (too conservative for this skill's aesthetic)
- Academic/lecture slides (different content density)
- Simple slide requests with no creative ambition (this skill assumes the user wants something distinctive)

## Core Principles

This skill is built around three principles of AI collaboration. They apply to every phase. See `references/ai-collaboration-principles.md` for the full rationale.

1. **Ask clarifying questions before building.** Never jump to implementation with thin context. The Phase 1 questionnaire is mandatory, not optional. Design first, code later.

2. **Store context outside the conversation.** Long iterative sessions lose context. After the user picks a style, write `PLAN.md` and keep it updated. Future-you (or future-LLM) will thank you.

3. **Show, don't tell.** When design preferences are hard to articulate, generate visual options. Never ask "serif or sans-serif?" Instead, show previews in both and let the user pick. Words fail; visuals succeed.

**And one aesthetic commitment**: make it stand out. The default hackathon submission is a bland console recording. Your job is to produce something memorable — bold typography, confident color choices, purposeful whitespace, character-driven narrative.

## Workflow Overview

This skill follows a 9-phase workflow (Phase 0 through 8). Full details: `references/workflow-phases.md`.

```
Phase 0 → Discover: User describes their hackathon project
Phase 1 → Clarify: Ask targeted questions about audience, timing, demos, branding
Phase 2 → Preview: Generate 5 style options (3 sample slides each)
Phase 3 → Build: Generate complete deck in chosen style
Phase 4 → Document: Create PLAN.md to store context (recommended)
Phase 5 → Iterate: Refine specific slides based on feedback
Phase 6 → Narrate: Generate AI narration script aligned to video length
Phase 7 → Integrate: Guide user through inserting recorded demo videos
Phase 8 → Submit: Package deliverables for the hackathon's submission format
```

## Key References

When executing this skill, load the relevant reference docs:

| Phase | Reference |
|-------|-----------|
| Phase 1 clarifying questions | `references/workflow-phases.md` |
| Phase 2 style presets | `references/style-presets.md` |
| Phase 2/3 slide patterns | `references/slide-patterns.md` |
| Phase 3 HTML scaffolding | `assets/style-preview-template.html` |
| Phase 4 plan.md generation | `assets/plan-template.md` |
| Phase 5 iteration patterns | `references/iteration-patterns.md` |
| Phase 6 script generation | `assets/narration-script-template.md` |
| Phase 7 video integration | `references/video-integration.md` |
| Phase 8 submission checklist | `references/workflow-phases.md` |

## Output Conventions

All files produced by this skill live in a single directory, typically `<project>/slides/`:

```
slides/
├── PLAN.md                    — captured hackathon context + slide breakdown
├── <project>-deck.html        — single-file HTML deck, zero dependencies
├── narration-script.md        — per-slide AI narration script
└── [recorded video files]     — user's OpenScreen / QuickTime captures
```

Produced files are:

- **HTML decks**: Single file, inline CSS/JS, zero npm/build dependencies. Uses Google Fonts via CDN.
- **Navigation**: Arrow keys + click halves + nav dots. Standard across all styles.
- **Animations**: CSS keyframes with staggered delays. No motion libraries.
- **Responsive**: Viewport-fitting with `clamp()`. Usable in any browser without setup.

## What Makes This Different From Other Slide Skills

Most slide generators converge on generic aesthetics (Inter font, white backgrounds, purple gradients). This skill explicitly rejects that. Every deck generated should:

- Commit to **one** aesthetic direction (not hedge with "safe" choices)
- Use **distinctive typography** (not Inter, not Roboto, not Arial)
- Include **character and narrative** when possible (mascots, day-in-the-life, use cases)
- Reserve space for **live demo video** integration (hackathon demos always have one)
- Provide an **AI narration script** (most hackathon submissions use AI voice, not human voiceover)

## Important Behaviors

- **Don't skip Phase 1.** Even if the user seems in a hurry, ask clarifying questions. The quality of the final deck is bounded by the quality of context gathered here.
- **Don't hardcode colors in style presets.** Let the chosen aesthetic direction guide color choices, but pick colors that match the user's hackathon theme or a beautiful theme-agnostic palette — don't default to the same hex values every time.
- **Don't use emojis in user-facing output unless the user requests them.** But emojis ARE appropriate inside slide content (as visual elements), since the user is explicitly asking for visually rich slides.
- **Don't generate the PLAN.md before the user picks a style.** Plan generation comes AFTER style selection — that way the plan captures the actual chosen direction, not speculation.
- **Always match the narration script length to the user's stated video length.** 3 minutes ≠ 5 minutes. Word count matters.
