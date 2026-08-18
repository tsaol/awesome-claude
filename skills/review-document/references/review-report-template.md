# Review: {{document_name}}

**Reviewer:** {{reviewer}}
**Date:** {{date}}
**Authority domain:** {{whose official docs are authoritative — e.g. AWS, Kubernetes, PostgreSQL}}
**Retrieval method:** {{vendor docs MCP | WebSearch + WebFetch | URL constructed, content confirmed by fetch | repository grep}} — note any rung skipped because the tool was unavailable
**Coverage:** {{N}} claims extracted, {{N}} verified, {{N}} not checked ({{reason}}). Lifecycle/EOL checked for: {{components}}

---

## Prior Input

_Omit this section when there is no prior_input._

| # | Prior finding | Status | Notes |
|---|---|---|---|
| 1 | _finding from prior review_ | ✅ Already addressed / ⚠️ Still present / 🔄 Partially addressed | _details_ |

---

## Claim Ledger

Every claim extracted from the document, with its verdict. Counts here MUST match the counts in the Recommendation.

| ID | Claim | Location | Verdict |
|---|---|---|---|
| C1 | _atomic claim as stated in the document_ | _§ heading or line_ | 🔴 Incorrect |
| C2 | _atomic claim_ | _§ heading or line_ | ✅ Correct |
| C3 | _atomic claim_ | _§ heading or line_ | ⚪ Unverifiable |

---

## 🔴 Critical Findings

_Keep this heading even when empty; write `_None._` under it._

### 1. [{{Incorrect | Fabricated | Contradictory | EOL/Deprecated}}] {{title}}

**Claim:** {{C1}} — _quote from document_

**Actual:** _verified fact_

**Source:** [source title, specific section](url)

**Action:** _specific fix instruction_

---

## 🟡 Medium Findings

_Keep this heading even when empty; write `_None._` under it._

### 1. [{{Imprecise | Wrong source | Scope-mismatched}}] {{title}}

**Claim:** {{C4}} — _quote from document_

**Actual:** _verified fact_

**Source:** [source title, specific section](url)

**Action:** _specific fix instruction_

---

## ⚪ Unverifiable

Claims that no authoritative source settled. These are findings, not passes. Keep this heading even when empty; write `_None._` under it.

### 1. {{title}}

**Claim:** {{C3}} — _quote from document_

**Searched:** _which pages and search terms were tried, and what came back_

**Why unresolved:** _no official page covers it / sources ambiguous / no vendor docs exist for this system_

**Action:** _who or what can settle it — config path to read, team to ask, or drop the number and keep the qualitative statement_

---

## ✅ Verified Correct

- **{{C2}}** _claim_ — [source, section](url)

---

## Recommendation

**Summary:** _X 🔴, Y 🟡, Z ⚪, W ✅ — total must equal the claim ledger row count_

**Safe to share:** _which sections stand as-is_

**Needs rework:** _which sections, and what breaks if shared unchanged_

**Structural assessment:** _customer-facing documents only — does it establish the reader's situation and goal before presenting solutions? Omit for internal notes and reference material._

**Priority actions:**
1. _most critical fix_
2. _next fix_
3. _next fix_
