# Three Principles of AI Collaboration

These principles are the foundation of this skill. They emerged from real experience building a hackathon deck with an LLM, and they turn out to be generalizable to any creative AI collaboration.

Apply them in every phase of this skill. When in doubt, return to these.

---

## Principle 1: Ask Clarifying Questions Before Building

**The rule**: Never jump to implementation when context is thin. Ask questions first.

**Why**: An LLM with thin context will default to generic output. Generic slides look like every other AI-generated slide. A good clarifying-questions phase reveals constraints the user didn't realize matter: the audience, the time limit, the awards being targeted, whether there's a mascot, whether live demos are involved.

**How to apply in this skill**:

- Phase 1 is mandatory. Do not skip it even when the user seems impatient.
- Ask questions in batches of 3-6, not one at a time.
- Prefer specific over generic: "What's the video time limit?" beats "Tell me about your hackathon."
- After receiving answers, restate your understanding before proceeding. This catches misalignments before they become wasted work.

**What the user will notice**: The first 5 minutes of the conversation feel like an interview. That's intentional. The quality of everything downstream depends on this.

---

## Principle 2: Store Context Outside the Conversation

**The rule**: Persist decisions and context in markdown files, not in conversation history.

**Why**: Long iterative sessions lose context — both for the user (who forgets what was decided) and for the LLM (whose context window gets summarized or truncated). Markdown files are durable, editable, and can be re-read in future sessions to pick up where you left off.

**How to apply in this skill**:

- After the user picks a style (Phase 3), generate `PLAN.md` that captures:
  - Hackathon event name, time limit, audience
  - Team info
  - Product one-liner and key messages
  - Chosen style direction and why
  - Slide-by-slide breakdown with timing
  - Video insertion points
- Update `PLAN.md` whenever major decisions change (style pivot, new slide added, different ordering).
- Reference `PLAN.md` when iterating — don't rely on conversation memory to remember what was decided.
- The narration script (`narration-script.md`) is another form of context-outside-conversation.

**What the user will notice**: After a long session of tweaks, they can close the browser tab, come back a week later, and still understand what the deck is about just by reading the markdown files.

---

## Principle 3: Show, Don't Tell

**The rule**: When a user can't articulate their aesthetic preference, generate visual options and let them pick.

**Why**: Design preferences are hard to describe in words. "Modern but not sterile." "Warm but professional." "Bold without being too loud." These descriptions don't converge on a specific visual. But show a user three renderings and they'll instantly know which one resonates.

**How to apply in this skill**:

- Phase 2 is mandatory: generate 5 style previews (3 sample slides each) before committing to a direction.
- Each preview should be **visually distinct** from the others — not variations on one theme. One should be dark, one warm editorial, one bold and bright, one elegant, one unexpected.
- Do not ask "do you want serif or sans-serif?" Instead, show a preview with serif and a preview with sans-serif.
- When the user rejects a preview, ask what *specifically* they disliked and use that signal in future iterations. "Too dark" is useful feedback; "I don't know, something else" is not.

**What the user will notice**: They get to make real design decisions without needing design vocabulary. The LLM handles the translation from visual instinct to HTML/CSS.

---

## How the Three Principles Reinforce Each Other

- **Clarifying questions** inform the 5 style previews (Principle 3 depends on Principle 1).
- **Stored context** in PLAN.md makes future iterations cheaper — the LLM doesn't re-ask questions it already asked (Principle 2 compounds over time).
- **Visual previews** reveal preferences the user couldn't articulate in the clarifying-questions phase — new information flows back into the plan (Principles 3 and 2 feed each other).

These are not three separate rules. They're three sides of the same approach: **treat the user as a creative decision-maker, and treat the LLM as an implementer that needs sharp context and visible options to do its best work.**

---

## When to Reference These Principles

- **Start of a new session**: Re-read these principles to reset the approach.
- **When tempted to skip Phase 1 or Phase 2**: These are the guardrails that prevent generic output.
- **When the user is frustrated**: Often the root cause is a missed clarifying question or a preview that wasn't shown. Go back to the principles.
- **When adding new features to this skill**: Ask "does this honor the three principles, or shortcut them?" Shortcuts accumulate into generic output.
