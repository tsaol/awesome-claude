---
name: docgen
description: >
  Generate documents (PPTX, DOCX, PDF, XLSX, HTML) via AWS Bedrock AgentCore Runtime.
  Use this skill when the user asks to:
  - Generate a PPT/presentation / 生成PPT
  - Generate a Word document / 生成Word文档
  - Generate a PDF / 生成PDF
  - Generate an Excel spreadsheet / 生成Excel表格
  - Generate a frontend HTML page / 生成前端页面
  - Convert an article to a presentation / 把文章转成PPT
  - Create a document from a topic / 根据话题生成文档
  This skill uses AWS Bedrock AgentCore Runtime (cloud-based, Claude + Code Interpreter).
license: MIT
---

# Document Generation via AgentCore Runtime

## Overview

This skill generates professional documents by calling an **AWS Bedrock AgentCore Runtime** agent. The remote agent uses Claude + Code Interpreter to produce high-quality files — no local office software required.

## Supported Document Types

| Type | Flag | Output | Use Case |
|------|------|--------|----------|
| pptx | `--type pptx` | PowerPoint | Presentations, tech talks |
| docx | `--type docx` | Word | Reports, design docs |
| pdf | `--type pdf` | PDF | Invoices, formal documents |
| xlsx | `--type xlsx` | Excel | Data tables, KPI tracking |
| frontend-design | `--type frontend-design` | HTML | Dashboards, landing pages |

## Prerequisites

1. **AWS credentials** configured (`~/.aws/credentials`, env vars, or IAM role)
2. **AgentCore Runtime** deployed with document generation agent
3. **Python 3.10+** with `boto3` installed

### Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock-agentcore:InvokeAgentRuntime",
      "Resource": "<your-runtime-arn>"
    }
  ]
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RUNTIME_ARN` | Yes | AgentCore Runtime ARN |
| `AWS_REGION` | No | AWS region (default: `ap-northeast-1`) |

The script also auto-loads `.env` from `~/codes/document-generation-mcp/.env` if present.

## Quick Start

```bash
# Generate a PowerPoint
python scripts/docgen.py --type pptx \
  --prompt "Create a 10-slide presentation about cloud computing" \
  --output presentation.pptx

# Generate a Word document
python scripts/docgen.py --type docx \
  --prompt "Write a technical design document about microservices" \
  --output design.docx

# Generate from a prompt file (for long prompts)
python scripts/docgen.py --type pptx \
  --prompt-file my-prompt.txt \
  --output slides.pptx

# Large PPT (15+ slides) — auto-splits into parallel batches
python scripts/docgen.py --type pptx \
  --prompt-file 22-slide-prompt.txt \
  --output big-deck.pptx

# Force single-batch mode (disable auto-split)
python scripts/docgen.py --type pptx \
  --prompt-file prompt.txt \
  --output output.pptx \
  --no-split --timeout 1800
```

## Python API

```python
from scripts.docgen import generate

result = generate(
    skill_type="pptx",
    prompt="Create a 12-slide deck about AI trends in 2026",
    output_path="output/ai-trends.pptx",
)

if result["success"]:
    print(f"Saved: {result['path']} ({result['size']} bytes, {result['elapsed']:.0f}s)")
else:
    print(f"Error: {result['error']}")
```

## How Claude Code Should Use This Skill

When a user asks to generate a document, follow this workflow:

### Step 1: Determine the Mode

- **Mode A (Article -> Document)**: User has an existing article/markdown and wants it converted
- **Mode B (Topic -> Document)**: User provides a topic and wants a document from scratch

### Step 2: Construct the Prompt

The prompt quality determines the output quality. Follow these guidelines:

#### PPTX Prompt Template

```
Create a [N]-slide professional presentation about [topic].
Use [color scheme] with [text color] on [background color].

IMPORTANT: Every slide MUST include speaker notes. Add speaker notes using
the python-pptx notes_slide feature: slide.notes_slide.notes_text_frame.text = "notes content".
Speaker notes should be 80-150 words per slide, written in conversational style,
explaining the key talking points. Do NOT just repeat the bullet points.

Slide 1: Title - [title], [subtitle]
Slide 2: [Section] - [key point 1], [key point 2], [key point 3]
Slide 3: [Section] - [data table or key facts]
...
Slide N: Thank You - [closing info]
```

**PPTX Rules**:
- Each slide description should be under 50 words (keywords and data, not paragraphs)
- Total slides should be <= 22 (more affects generation quality)
- Use "table with N rows" for data tables
- Always include speaker notes instructions
- Specify color scheme explicitly

#### DOCX Prompt Template

```
Create a professional [document type] about [topic].
Include sections: [section list].
Section 1: [Title] - [content points]
...
```

#### XLSX Prompt Template

```
Create an Excel spreadsheet for [purpose].
Sheet 1: [name] - columns: [col1], [col2], ...
Sheet 2: [name] - [description]
```

### Step 3: Save the Prompt (Optional)

For debugging and reuse, save the prompt to a file:

```bash
# Save to prompt file
cat > prompt.txt << 'EOF'
[your prompt here]
EOF
```

### Step 4: Generate the Document

```bash
python <skill-path>/scripts/docgen.py \
  --type pptx \
  --prompt-file prompt.txt \
  --output output/presentation.pptx
```

**Expected generation times**:
- HTML: 30s - 1min
- PPTX (<=10 slides): 2-5 min
- PPTX (10-22 slides): 3-15 min
- DOCX/PDF: 2-5 min
- XLSX: 2-4 min

Complex presentations (15+ slides with detailed content) can take 10-25 minutes.
The default timeout is 1200s (20 min). Use `--timeout 1800` for very complex documents.

### Step 5: Verify Output

Check that the file was generated and report the result:
```bash
ls -la output/presentation.pptx
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--type` | | Document type: docx, pdf, pptx, xlsx, frontend-design (required) |
| `--prompt` | | Document description (inline) |
| `--prompt-file` | | Read prompt from file |
| `--output` | `-o` | Output file path (required) |
| `--region` | | AWS region (default: ap-northeast-1) |
| `--runtime-arn` | | AgentCore Runtime ARN |
| `--timeout` | | Read timeout in seconds (auto-estimated if omitted) |
| `--no-split` | | Disable auto-split for large PPTX |
| `--max-slides-per-batch` | | Max slides per batch when splitting (default: 11) |

## Tips for Better Results

1. **Be specific about colors**: Always provide hex codes, not just color names
2. **Keep slide content concise**: Keywords and data points, not full sentences
3. **Speaker notes matter**: Include the speaker notes instruction for PPTX — it dramatically improves presentation quality
4. **Chinese content**: Specify "All slide titles and content MUST be in Chinese" if needed
5. **Data tables**: Describe as "table: col1, col2, col3" with row data
6. **Complex prompts**: Save to a file with `--prompt-file` instead of inline `--prompt`
7. **Respect the 20-call budget**: The server agent has a hard limit of 20 tool calls (code executions). Keep each slide description under 50 words so the agent can generate everything in 1-2 code runs
8. **Auto-split threshold**: For 15+ slides, the script auto-splits into ≤11-slide batches. This is more reliable than generating 22 slides in one shot

## Troubleshooting

### Timeout Errors

The script now auto-estimates timeout based on complexity. If you still hit timeouts:

```bash
# Explicit timeout override
python scripts/docgen.py --type pptx --prompt-file prompt.txt --output out.pptx --timeout 2400

# Better: let auto-split handle it (15+ slides splits into parallel batches)
python scripts/docgen.py --type pptx --prompt-file prompt.txt --output out.pptx
```

The script retries up to 3 times on transient errors (timeout, connection reset) with exponential backoff.

### RUNTIME_ARN Not Configured

Set the environment variable or pass via CLI:

```bash
export RUNTIME_ARN="arn:aws:bedrock-agentcore:ap-northeast-1:123456789:runtime/your-agent-id"
python scripts/docgen.py --type pptx --prompt "..." --output out.pptx
```

Or create a `.env` file at `~/codes/document-generation-mcp/.env`:

```
AWS_REGION=ap-northeast-1
RUNTIME_ARN=arn:aws:bedrock-agentcore:ap-northeast-1:123456789:runtime/your-agent-id
```

### Empty or Failed Response

The AgentCore agent has a **20 tool call budget** (enforced by MaxToolCallsHook on the server). If the prompt is too complex, the agent runs out of calls before producing the file. Symptoms:
- Response with no `file_base64`
- Error: "Code Interpreter did not produce an output file"

Solutions:
- Reduce slide count (keep ≤ 11 per batch, the auto-split handles this)
- Simplify per-slide content (use keywords, not paragraphs)
- The agent must: install deps (1 call) + generate file (1 call) + output base64 (1 call) = 3 minimum calls, leaving 17 for error recovery

### Understanding Server Constraints

The remote agent operates under these constraints:
- **Model**: Claude Opus 4.6 (cross-region inference profile)
- **Tool call limit**: 20 code executions maximum (warning at 19, hard-stop at 21)
- **Conversation window**: SlidingWindowConversationManager (window=20, per_turn=True) — old messages get trimmed
- **Base64 capture**: A hook captures file output before conversation trimming
- **Retry on server**: The agent retries transient Bedrock errors up to 3 times internally

## Architecture

### Current Mode (Synchronous)

```
User / Claude Code
       |
       | python scripts/docgen.py --type pptx --prompt "..."
       |
       v
  boto3 invoke_agent_runtime()  ←── retry with backoff on transient errors
       |
       v
  AWS Bedrock AgentCore Runtime
       |
       | Strands Agent + Claude Opus 4.6 + Code Interpreter
       | MaxToolCallsHook (20 calls) + Base64CaptureHook
       |
       v
  Generated file (base64 encoded in response)
       |
       v
  Decoded and saved to --output path
```

### Auto-Split Mode (for 15+ slide PPTX)

```
User / Claude Code
       |
       | python scripts/docgen.py --type pptx --prompt-file big.txt -o deck.pptx
       |
       v
  _count_slides_in_prompt() → 22 slides detected
       |
       v
  _split_pptx_prompt() → [Batch 1: slides 1-11, Batch 2: slides 12-22]
       |
       v
  ThreadPoolExecutor (parallel)
       ├── generate("pptx", batch1) → Part1.pptx
       └── generate("pptx", batch2) → Part2.pptx
       |
       v
  _merge_pptx_files([Part1.pptx, Part2.pptx]) → deck.pptx
```

### Production Mode (Async — for team/service deployments)

For production use with Amazon Quick Suite, see the full async architecture in
`sample-amazon-quick-suite-knowledge-hub/docs/use-cases/document-generation-mcp-agentcore-runtime/`.

This uses: submit_job Lambda → fire-and-forget → Step Function polling → direct-persist to S3 → CloudFront download URL. No client-side timeout concerns.
