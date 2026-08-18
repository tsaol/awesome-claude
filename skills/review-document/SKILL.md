---
name: review-document
description: >-
  Fact-check technical documents against official vendor documentation. Extracts atomic claims,
  verifies each against an authoritative source, reports findings with severity and citations.
  Use when the user says "review document", "fact-check", "verify this doc", "prüfe", "check for errors".
  Verification only — never edits the document.
---

# Review Document

## Overview

Fact-checks a technical document by decomposing it into atomic claims, verifying each against authoritative vendor documentation, and reporting findings with severity tiers and source citations.

The method is **decompose → verify → report**. Decomposing into atomic claims before verifying is what makes the review auditable: the reader can see which claims were checked, which source settled each one, and which could not be settled at all.

**This skill verifies; it never edits.** It also never computes an aggregate quality score — a document with 19 correct claims and one wrong service limit is not "95% good", it is a document with a blocking error.

## Parameters

- **input_path** (required): File or directory to review
- **prior_input** (optional): Prior review notes / collaborator feedback to reconcile against the current version
- **source_policy** (optional, default `public-only`): `public-only` restricts citations to public vendor docs and blogs; `include-internal` also searches internal sources
- **output_path** (optional): Where to write the report. Defaults to the input file's directory
- **email_draft** (optional, default `false`): Draft a summary email after the review

## Core principle: fail loud

An unverifiable claim is a **finding**, not a default verdict. When a lookup fails, the tool is missing, the page 404s, or the sources are ambiguous, you MUST report ⚪ Unverifiable and say why — you MUST NOT resolve uncertainty into ✅ or 🔴.

**Why:** a fact-checker that silently guesses is worse than none, because the reader trusts it. "I could not confirm this" is a useful result; a fabricated verdict discredits every other line in the report.

## Workflow

### 1. Load documents

**Constraints:**
- You MUST support `.md`, `.txt`, `.docx`, `.pdf`, `.html`, `.rst`, `.adoc`
- For `.docx`: `python3 -c "from docx import Document; ..."`. For `.pdf`: `python3 -c "import pymupdf; ..."`. Others: read as text
- If either library is missing, you MUST install it (`pip install python-docx` / `pymupdf`) rather than skipping the file
- For a directory, discover all supported files; for a single file, read it completely
- You MUST list the documents found and confirm with the user before proceeding
- You MUST NOT process more than 10 documents per run because quality degrades with volume — suggest batching
- If **prior_input** is given, check each prior finding against the current text and assign: ✅ Already addressed | ⚠️ Still present | 🔄 Partially addressed

### 2. Identify the authority domain

Before extracting claims, decide **whose documentation is authoritative** for this document.

**Constraints:**
- You MUST detect the vendor/technology the document is about (AWS, Azure, GCP, Kubernetes, PostgreSQL, a language runtime, an internal platform, …) and name it in the report header
- The authoritative source is that vendor's **official documentation**, then its official blog, then its release notes / changelog. Community content (Stack Overflow, Medium, personal blogs) is NEVER authoritative — a claim supported only by community content is 🟡 Wrong source
- For AWS documents you MUST prefer the AWS Documentation MCP tools when they are connected (`aws___search_documentation`, `aws___read_documentation`, and `aws___get_regional_availability` for regional claims); when they are not, drop to the retrieval ladder in step 4
- If a document spans several vendors, you MUST verify each claim against its own vendor's docs
- If no authoritative source exists for the subject matter (internal-only system with no docs), you MUST say so and expect most claims to land in ⚪ Unverifiable rather than forcing verdicts

### 3. Decompose into atomic claims

Split the document into individually checkable claims. This is the step that makes the review auditable.

**Constraints:**
- Each claim MUST be **atomic** — one assertion, independently checkable. Split compound sentences: "Lambda runs 15 minutes and costs $0.20 per million requests" is two claims
- The test for atomicity is that **one source lookup settles it**. If verifying a claim would need two different pages, split it; if two claims always resolve from the same sentence of the same page, merge them. Do not split for the sake of a longer ledger — the ledger is evidence of coverage, not a volume metric
- Each claim MUST carry a stable ID (`C1`, `C2`, …) and its location (section heading or line number) so findings can be traced back
- You MUST extract claims about: capabilities and features; numeric limits and quotas; pricing; regional and version availability; default behaviors; EOL / deprecation status of anything named
- You MUST check every named model, service, runtime, or API version for EOL/deprecation even when the document says nothing about its lifecycle, because recommending a dead component is a serious defect. This check does **not** create ledger rows: the ledger holds only claims the document actually makes. Raise a 🔴 EOL/Deprecated finding **only** when something is genuinely past or near end-of-life, and note the lifecycle check in the Coverage line rather than adding a row per component
- You SHOULD skip subjective statements, opinions, and recommendations that no source can settle. If a "best practice" claim is attributed to the vendor, it IS checkable — verify the attribution
- You MUST record the claim ledger in the report (see template). The ledger is the evidence that the review was systematic
- You MUST NOT modify the source document

### 4. Verify each claim

**Constraints:**
- You MUST reach an actual source for every claim. Plausibility is not verification — if it sounds right but you have no source, it is ⚪ Unverifiable
- **Retrieval ladder** — use the highest rung available, and record which rung in the report's **Retrieval method** header:
  1. Vendor documentation MCP tools (e.g. `aws___search_documentation`)
  2. `WebSearch` + `WebFetch` scoped to the vendor's official docs and blog domains
  3. `WebFetch` on a constructed official-docs URL — allowed only if the fetched page actually states the fact. A guessed URL that 404s or omits the claim is NOT a verification; record `URL constructed, content confirmed by fetch`
  4. Nothing available → ⚪ Unverifiable, with the reason
- Record the rung you actually reached, and note when a rung was **skipped because the tool was unavailable** rather than because a higher rung succeeded — otherwise every review in a tool-poor environment reports rung 3 and understates its own rigor
- Rungs 1–3 assume the subject has a vendor whose docs domain you can name. For **internal or unnamed systems there is no such domain**, so the ladder does not apply. In that case, in this order:
  1. **Grep the repository first.** Code and config are authoritative for their own behavior. Cite `file:line`. This usually settles the claim outright and is cheaper than any search
  2. If the repo has no answer, try one open web search to establish the term has no public documentation, and report what came back. Search engines frequently block automated fetches — if they do, record that and move on. A blocked engine is not a reason to keep retrying
  3. Only when neither code nor docs are reachable is the claim ⚪
- When citing a repository you MUST state which repo/path you searched and confirm it is the codebase the document describes, because a same-named module in an unrelated project proves nothing
- You MUST capture the source URL **and** the specific section or table for every verdict
- For pricing, model, and regional-availability claims you MUST cross-reference at least two official sources, because vendors' own pages disagree more often than readers expect. This applies to claims whose **value varies by region or tier** — a globally fixed limit stated in a region-scoped document is not a regional claim
- For hard limits and quotas, one official page is sufficient — but **absence from the quotas page does not disprove a limit**. Quotas pages often cover only adjustable, throughput-style quotas, while fixed structural caps live on a constraints, limits, or developer-guide page. You MUST check at least one other official page before recording ⚪ for a limit, because a premature ⚪ reads as "undocumented" when the limit is in fact firm
- When two official sources **covering the same platform and scope** disagree you MUST report 🔴 Contradictory with both URLs rather than silently picking one, because the reader may check the other. Different platforms publishing different values for the same thing is NOT a contradiction — a vendor's managed-service EOL date legitimately differs from the model provider's own date, and a per-region price legitimately differs from the us-east-1 price. Report those as ✅ against the source that matches the document's stated scope, or 🟡 Scope-mismatched if the document cites the wrong one
- You SHOULD verify claims in parallel with subagents when there are more than ~8 claims, since each lookup is independent. You MUST NOT let a subagent's summary stand as the verdict without the source URL it used
- If **source_policy** is `include-internal` you MAY search internal sources; if the internal tooling is unavailable, continue with public sources and note it
- Under `public-only` you MUST NOT cite confidential or internal material, because the report may be shared externally
- You MUST log any claim you deliberately did not check (out of scope, sampling, truncation) — silent omission reads as "everything was covered"

### 5. Classify findings

**Constraints:**
- You MUST assign each claim exactly **one** severity, so the counts sum to the number of claims in the ledger. A claim that is technically right but misleading belongs in 🟡 only — not also in ✅:
  - 🔴 **Incorrect** — wrong number, date, percentage, or fact
  - 🔴 **Fabricated** — the feature or behavior does not exist at all
  - 🔴 **Contradictory** — two official sources disagree
  - 🔴 **EOL/Deprecated** — named thing is past or near end-of-life and the document does not say so
  - 🟡 **Imprecise** — correct but misleading, or missing nuance that changes a decision
  - 🟡 **Wrong source** — correct, but cited from non-authoritative content
  - 🟡 **Scope-mismatched** — right for one region/tier/version, wrong for the one the document targets
  - ⚪ **Unverifiable** — no authoritative source settles it. MUST state what was searched and what came back
  - ✅ **Correct** — confirmed against an authoritative source
- You MUST prefix each finding title with its subtype, e.g. `### 1. [Fabricated] GraphRAG available in every region`
- You MUST distinguish Incorrect from Fabricated, because a wrong number is a find-and-replace while an invented feature requires deleting a section and rethinking the surrounding argument
- Every 🔴, 🟡, and ⚪ finding MUST have a concrete **Action** line naming what to change: "Replace 500 KB → 400 KB", "Delete the row"
- For ⚪ the Action MUST name **who or what can settle it** — the config file or code path to read, the team or vendor to ask, or an instruction to drop the specific number and keep the qualitative statement. "Ask the vendor" is not actionable for an internal system with no vendor

### 6. Write the report

**Constraints:**
- You MUST follow `references/review-report-template.md`
- Order: Prior Input verdicts (if any) → Claim Ledger → 🔴 → 🟡 → ⚪ → ✅ → Recommendation
- You MUST keep every severity heading even when it is empty, writing `_None._` under it, because a missing heading is indistinguishable from an overlooked tier
- The ledger row count MUST equal the sum of the severity counts. You MUST state both in the Recommendation so the reader can check the arithmetic
- The **Recommendation** MUST state which sections are safe to share as-is, which need rework, and a numbered priority list
- If the document is **customer-facing or externally shared**, the Recommendation MUST also assess whether it establishes the reader's situation and goal before presenting solutions, and flag jumping straight to architecture ("working backwards"). You MUST skip this for internal notes, scratch files, and reference material, because structural coaching on a personal scratchpad is noise
- The ✅ section MUST list what was confirmed, because a review that shows only failures gives the reader no way to judge its coverage
- Write to `review-<document-name>.md` (kebab-case) in **output_path**; for directories use `review-<directory-name>.md`
- You MUST report counts in chat afterwards: 🔴 / 🟡 / ⚪ / ✅ and the file path

### 7. Draft email (optional)

**Constraints:**
- Draft inline — do NOT send or save it, because the user reviews first
- Cover 🔴, 🟡, and ⚪ findings with source links; do not enumerate every ✅
- Write constructively — the goal is a usable fix list, not a verdict on the author

## Examples

### Review a directory

```
input_path: "/path/to/docs/"
source_policy: "public-only"
```

Trigger: "Bitte prüfe alle Dokumente in diesem Ordner auf Korrektheit."

### Single document with email

```
input_path: "/path/to/bedrock-overview.md"
email_draft: true
```

Trigger: "Review this document and draft an email with the findings."

### Reconcile a prior review

```
input_path: "/path/to/document.docx"
prior_input: "/path/to/colleague-feedback.md"
```

Trigger: "Review this doc — incorporate the feedback from the prior review."
