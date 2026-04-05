---
name: ppt-speech-script
description: "Generate a speech script from an existing PowerPoint presentation. Use this skill when the user has a .pptx file and wants a speaker script, presentation notes, or talk script to accompany it. Triggers on: 'speech script', 'speaker notes', 'talk script', 'presentation script', '演讲稿', '讲稿'"
license: Proprietary. LICENSE.txt has complete terms
---

# PPT Speech Script Generator

Generate a structured, oral-style speech script from an existing PowerPoint presentation.

## When to Use

- User has an existing `.pptx` file and wants a speech script to go with it
- User says: "generate a speech script", "write speaker notes", "写演讲稿", "生成讲稿"
- This is NOT for creating PPT files — use the `pptx` skill for that

## Workflow

### Step 1: Extract Content

Extract text, visual layout, and embedded images from the presentation using three methods in parallel:

**Text extraction:**
```bash
python3 -m markitdown <pptx_file>
```

**Visual layout (thumbnail grid):**
```bash
python3 skills/pptx/scripts/thumbnail.py <pptx_file> <output_dir>/thumbnails --cols 5
```

**Image extraction (unpack media files):**
```bash
python3 skills/pptx/ooxml/scripts/unpack.py <pptx_file> <output_dir>/unpacked
```

Then:
1. Read the thumbnail grid image(s) to understand the visual structure of each slide
2. Build a **slide-to-image mapping** by reading the relationship files:
   - Parse `ppt/slides/_rels/slideN.xml.rels` for each slide
   - Extract `Target="../media/imageX.ext"` references to find which images belong to which slide
3. For slides with important images (charts, architecture diagrams, screenshots), **read the original image** from `ppt/media/` using the Read tool for detailed visual analysis
   - Skip generic/decorative images (backgrounds, logos, icons) — focus on content-carrying images
   - Prioritize: architecture diagrams, data charts, comparison tables, workflow diagrams, product screenshots

**Image analysis guidelines:**
- For **architecture/flow diagrams**: describe the components, data flow direction, and key relationships
- For **data charts**: read exact numbers, axis labels, and trends
- For **comparison tables**: extract the key differentiators
- For **product screenshots**: describe what the user interface shows
- For **photos/decorative images**: brief description only, don't over-analyze

This image analysis enables the speech script to accurately describe visual content that `markitdown` cannot capture (since markitdown only extracts text, not image content).

### Step 2: Analyze Presentation Structure

Before writing, analyze the deck:

1. **Identify sections** — group slides into logical sections (intro, body sections, conclusion)
2. **Identify hidden slides** — thumbnail.py reports hidden slides; exclude them from the script
3. **Identify slide types** — title, content, data, diagram, comparison, section divider, closing
4. **Note visual elements** — charts, images, diagrams that need verbal explanation
5. **Estimate timing** — allocate time per slide based on content density

**Timing guidelines:**
| Slide type | Suggested time |
|------------|---------------|
| Title/cover | 30s - 1min |
| Agenda | 30s - 1min |
| Section divider | 15 - 30s |
| Content (light) | 1 - 1.5min |
| Content (dense) | 1.5 - 2.5min |
| Data/chart | 1.5 - 2min |
| Diagram/architecture | 2 - 3min |
| Demo/code | 2 - 3min |
| Summary | 1 - 2min |
| Closing/Q&A | 30s |

### Step 3: Write the Speech Script

Generate a complete speech script following these principles:

#### Output Format

```markdown
---
title: "PPT Title — Speech Script"
slides: <total visible slides>
estimated_time: "XX-XX minutes"
audience: "<target audience>"
---

# PPT Title — Speech Script

> Audience: <target audience> | Date: <date if available>

Estimated duration: XX minutes (including Q&A). Suggested time per slide is noted in brackets.

---

## Slide 0 — Slide Title [30s]

Speech content here...

---

## Slide 1 — Slide Title [1min]

Speech content here...

---

...

## Predicted Q&A

### Q1: <likely question>?
Answer key points...

### Q2: <likely question>?
Answer key points...

### Q3: <likely question>?
Answer key points...
```

#### Writing Principles

1. **Oral style** — Write as if speaking to the audience, not reading a document
   - Use conversational connectors: "Let's look at...", "The key takeaway here is...", "Now, moving on to..."
   - Avoid academic or written-style phrasing

2. **Don't read the bullets** — The script should EXPLAIN and EXPAND on slide content, not repeat it
   - Slide says "Cost reduced 34.8%" → Script says "We brought per-query cost down by over a third — from 9 cents to under 6 cents. At million-user scale, that's millions of dollars saved per month."

3. **Per-slide length**: 80-200 words (Chinese) or 60-150 words (English)
   - Section dividers and title pages: shorter (30-60 words)
   - Dense data or architecture slides: longer (150-250 words)

4. **Smooth transitions** — Each slide's script should naturally flow from the previous one
   - End of previous slide's conclusion → Beginning of next slide's topic
   - Use transitional phrases: "That brings us to...", "With that context in mind...", "So how do we solve this?"

5. **Highlight key points** — Use bold or verbal cues for emphasis
   - "The **most important** number on this slide is..."
   - "If you remember one thing from today..."

6. **Explain visuals** — For charts, diagrams, and images, guide the audience through what they're seeing
   - "Looking at this architecture diagram, data flows from left to right..."
   - "The blue bars represent the baseline, and the orange bars are our optimized results..."

7. **Audience awareness** — Tailor depth and terminology to the stated audience
   - CTO audience → focus on strategic impact, cost, and scalability
   - Developer audience → focus on implementation details and code
   - Business audience → focus on ROI, user impact, and market context

8. **Q&A section** — Prepare 3-5 predicted questions
   - Include "tough but fair" questions the audience is likely to ask
   - Provide concise answer key points (not full scripts)
   - Consider the audience's perspective and concerns

#### Language

- **Default**: Match the language of the PPT content
- **User override**: If user specifies a language (e.g., "in Chinese", "in English"), use that
- **Mixed content**: If PPT has mixed languages, use the dominant language unless told otherwise

### Step 4: Save Output

Save the speech script to the same directory as the PPT file:

```bash
# Output path: same directory as input, named speech-script.md
<pptx_dir>/speech-script.md
```

If a `speech-script.md` already exists, ask the user before overwriting.

## Dependencies

These should already be available from the `pptx` skill:

- **markitdown**: `pip install "markitdown[pptx]"` — text extraction
- **thumbnail.py**: `skills/pptx/scripts/thumbnail.py` — visual layout analysis
- **unpack.py**: `skills/pptx/ooxml/scripts/unpack.py` — PPTX unpacking for media extraction
- **LibreOffice**: for PDF conversion (used by thumbnail.py)
- **Poppler**: for PDF-to-image conversion (used by thumbnail.py)

## Edge Cases

**Very large presentations (50+ slides):**
- Group consecutive similar slides into sections
- Summarize repetitive slides rather than scripting each individually
- Note in the script: "Slides X-Y cover [topic] — walk through highlights"

**Image-heavy / text-light slides:**
- Use the slide-to-image mapping to read original images from `ppt/media/` at full resolution
- Describe what the audience sees based on direct image analysis
- For images that cannot be read (e.g., unsupported format), fall back to thumbnail grid analysis
- Flag slides where content is still unclear: "[Note: This slide contains a visual element — verify description against actual slide]"

**Hidden slides:**
- Exclude from the main script
- Optionally note them at the end: "Note: Slides X, Y, Z are hidden and not included in this script"

**No text content (pure image deck):**
- Extract all images via unpack and read each one directly for full-resolution analysis
- Use thumbnail grid for overall slide layout understanding
- Generate descriptive narration based on per-image analysis
- Clearly note which descriptions are based on visual interpretation

## Quality Checklist

After generating the script, verify:

- [ ] Every visible slide has a corresponding section
- [ ] Slide numbering matches the PPT (0-indexed)
- [ ] Transitions between slides are smooth
- [ ] No bullet points are simply repeated verbatim
- [ ] Time estimates per slide are reasonable
- [ ] Total estimated time is realistic for the slide count
- [ ] Q&A section includes 3-5 relevant questions
- [ ] Language matches user's request or PPT's dominant language
