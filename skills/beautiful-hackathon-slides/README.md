# Beautiful Hackathon Slides

A Claude Code skill for creating **distinctive, production-grade hackathon demo decks** — not the typical black-console-screenshot technical demo, but startup-pitch-style presentations that actually look designed.

A collection of workflow, patterns, and principles for building bold pitch decks with AI assistance — captured here so anyone can reuse them.

## What This Does

- **Walks you through a proven 7-phase workflow** — from clarifying questions to final demo video integration
- **Shows, doesn't tell** — generates 5 visually distinct style previews instead of asking "what font do you want?"
- **Delivers single-file HTML decks** — zero dependencies, opens in any browser, responsive
- **Reserves explicit slots for live demo recordings** — hackathon decks always need them
- **Generates AI narration scripts** — matched to your video's time limit
- **Stores context in markdown files** — so long iteration sessions don't lose alignment

## Philosophy

This skill is built around three principles of AI collaboration:

1. **Ask clarifying questions before building** — never jump to implementation with thin context
2. **Store context outside the conversation** — markdown files outlast conversation windows
3. **Show, don't tell** — visual options beat verbal design descriptions

See [`references/ai-collaboration-principles.md`](references/ai-collaboration-principles.md) for the full rationale.

## Installation

Clone the skill into your Claude Code skills directory:

```bash
git clone https://github.com/Esther2524/beautiful-hackathon-slides.git ~/.claude/skills/beautiful-hackathon-slides
```

Plugin Marketplace publishing is coming soon. For now, use the git clone method above.

## Usage

Once installed, there are two ways to invoke the skill:

**Option 1: Just describe what you need (recommended)**

Claude will automatically detect that this skill applies based on your request:

```
"help me make a hackathon pitch deck"
"I need slides for my hackathon demo video"
"create a presentation for our hackathon submission"
```

**Option 2: Invoke directly with slash command**

If Claude doesn't automatically pick up the skill, you can invoke it explicitly:

```
/beautiful-hackathon-slides
```

Either way, the skill will walk you through the full workflow:

1. Ask a few targeted questions about your project
2. Generate 5 visually distinct style previews for you to choose from
3. Build a complete HTML deck in your chosen style
4. Write a `PLAN.md` to preserve context
5. Help you iterate specific slides
6. Generate an AI narration script
7. Guide you through inserting recorded demo videos
8. Package deliverables for submission

## Repository Structure

```
beautiful-hackathon-slides/
├── SKILL.md                              ← entry point, loaded by Claude Code
├── README.md                             ← this file
├── LICENSE                               ← MIT
├── references/
│   ├── ai-collaboration-principles.md    ← the three principles
│   ├── workflow-phases.md                ← detailed 7-phase workflow
│   ├── style-presets.md                  ← 5 aesthetic archetypes
│   ├── slide-patterns.md                 ← reusable slide pattern library
│   ├── iteration-patterns.md             ← common adjustments lookup
│   └── video-integration.md              ← recording + inserting demos
└── assets/
    ├── plan-template.md                  ← PLAN.md template
    ├── narration-script-template.md      ← narration script template
    └── style-preview-template.html       ← HTML scaffolding
```

## The 5 Style Presets

Each is an *aesthetic direction*, not a fixed color palette. The skill picks colors to fit your specific project.

| Preset | Feel | Best For |
|--------|------|----------|
| **Warm Editorial** | Light, serif, magazine-like | Human-centered products, emotional themes |
| **Cyber Terminal** | Dark, mono, hacker-precise | DevTools, infrastructure, AI platforms |
| **Citrus Punch** | Light, bold sans, energetic | B2C products, creative tools, gaming |
| **Electric Dusk** | Dark navy, clean sans, sleek | Enterprise, fintech, data platforms |
| **Pastel Chapters** | Light split-duotone, storytelling | Education, wellness, character narratives |

## License

MIT — use freely for personal or commercial projects. See [LICENSE](LICENSE).

## Author

Created by [Esther Wang](https://github.com/Esther2524). The workflow, patterns, and principles captured here emerged from personal experiments in collaborating with AI tools on design and storytelling projects.

## Contributing

Improvements welcome. If you use this skill and find an iteration pattern, slide pattern, or style preset missing, open a PR with:
- The new addition
- A one-line description of when to use it
- A note on why the existing patterns weren't sufficient
