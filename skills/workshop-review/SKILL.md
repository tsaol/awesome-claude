---
name: workshop-review
description: Audit an AWS Workshop Studio workshop against content, structure, bilingual, asset, link, and navigation best practices. Generates a structured review report with severity levels and a pass/fail verdict. Use before publishing or after major content changes.
---

# Workshop Review - AWS Workshop Studio Audit

## Overview

This skill performs a comprehensive audit of an AWS Workshop Studio workshop (Hugo-based, bilingual EN/ZH) by:
- Verifying directory structure, frontmatter, and weight ordering
- Checking bilingual (EN/ZH) content parity
- Auditing static asset hygiene (unused, broken, oversized)
- Validating internal/external link integrity
- Evaluating content quality (TODOs, alert syntax, service naming, code blocks)
- Checking navigation flow (weight order, next links, lab numbering)

## When to Use

Trigger `/workshop-review` when:
- You have finished writing or updating workshop content and want to audit before publishing
- You want to verify bilingual consistency after translation
- You need to check for broken references or unused assets
- Before `git push` to Workshop Studio to ensure quality

## Usage

```
/workshop-review                                    # Review current directory
/workshop-review ~/codes/workshop/hr-quicksuite     # Review specific workshop
/workshop-review --phase=assets                     # Run only one phase
/workshop-review --fix                              # Auto-fix simple issues
```

### Flag behavior

- **No flags**: Run all 7 phases
- **`--phase=<name>`**: Run only the named phase (structure, bilingual, assets, links, quality, navigation) plus Phase 7 (report)
- **`--fix`**: Run all phases, then auto-fix simple issues (missing language specifiers, trailing whitespace, common service name typos)

## Workflow

```
Workshop Directory
        |
   /workshop-review [path]
        |
+----------------------------------+
| Phase 1: Structure & Frontmatter |
|   - EN/ZH file pairs             |
|   - Frontmatter title/weight     |
|   - Weight ordering               |
|   - Orphan directories           |
+----------------------------------+
        |
+----------------------------------+
| Phase 2: Bilingual Consistency   |
|   - Heading count parity         |
|   - Image reference parity       |
|   - Alert count parity           |
|   - Code block parity            |
+----------------------------------+
        |
+----------------------------------+
| Phase 3: Asset Hygiene           |
|   - Referenced vs on-disk images |
|   - Unused & broken images       |
|   - Oversized images (>500KB)    |
|   - Debug/temp images            |
+----------------------------------+
        |
+----------------------------------+
| Phase 4: Link Integrity          |
|   - Internal cross-references    |
|   - Relative link targets        |
|   - :assetUrl directive usage    |
|   - Hardcoded WS URLs           |
+----------------------------------+
        |
+----------------------------------+
| Phase 5: Content Quality         |
|   - TODO/FIXME/TBD markers      |
|   - Empty sections               |
|   - Alert syntax validation     |
|   - AWS service name casing     |
|   - Code block language specs   |
|   - Markdown table syntax       |
+----------------------------------+
        |
+----------------------------------+
| Phase 6: Navigation Flow         |
|   - Weight ordering logic        |
|   - Next/continue links         |
|   - Lab numbering sequence      |
|   - Prerequisite references     |
+----------------------------------+
        |
+----------------------------------+
| Phase 7: Review Report           |
|   - Structured summary tables   |
|   - Severity-tagged issues      |
|   - Verdict: PASS/WARN/FAIL     |
+----------------------------------+
```

## Phase Details

### Phase 1: Structure & Frontmatter

Verify every content directory has proper files and frontmatter.

**1a. Discover workshop root and content directory:**

```bash
WORKSHOP_DIR="${1:-.}"
CONTENT_DIR="$WORKSHOP_DIR/content"

# Verify this looks like a workshop
if [ ! -f "$WORKSHOP_DIR/contentspec.yaml" ]; then
  echo "WARNING: No contentspec.yaml found. This may not be a Workshop Studio workshop."
fi

# Check what languages are declared
grep -A5 "localeCodes" "$WORKSHOP_DIR/contentspec.yaml" 2>/dev/null
```

**1b. Find all content directories and check for EN/ZH file pairs:**

```bash
# List all directories under content/
find "$CONTENT_DIR" -type d | sort

# For each directory, check for index.en.md and index.zh.md
for dir in $(find "$CONTENT_DIR" -type d | sort); do
  has_en="no"; has_zh="no"
  [ -f "$dir/index.en.md" ] && has_en="yes"
  [ -f "$dir/index.zh.md" ] && has_zh="yes"
  echo "$dir | EN=$has_en | ZH=$has_zh"
done
```

**1c. Verify frontmatter has title and weight:**

```bash
# Extract frontmatter from all index files
for f in $(find "$CONTENT_DIR" -name "index.en.md" -o -name "index.zh.md" | sort); do
  # Extract title and weight from YAML frontmatter
  title=$(sed -n '/^---$/,/^---$/{ /^title:/p }' "$f")
  weight=$(sed -n '/^---$/,/^---$/{ /^weight:/p }' "$f")
  echo "$f | $title | $weight"
done
```

**1d. Check weight ordering within each parent directory:**

```bash
# For each parent, list children sorted by weight
for parent in $(find "$CONTENT_DIR" -type d | sort); do
  children=""
  for child in "$parent"/*/; do
    [ -f "$child/index.en.md" ] || continue
    w=$(sed -n '/^---$/,/^---$/{ s/^weight: *//p }' "$child/index.en.md")
    children="$children$w $child\n"
  done
  [ -n "$children" ] && echo "--- $parent ---" && echo -e "$children" | sort -n
done
```

**1e. Find orphan directories (directories with no index files):**

```bash
for dir in $(find "$CONTENT_DIR" -type d | sort); do
  [ "$dir" = "$CONTENT_DIR" ] && continue
  if [ ! -f "$dir/index.en.md" ] && [ ! -f "$dir/index.zh.md" ]; then
    # Only flag if directory has no subdirectories with content either
    has_child_content=$(find "$dir" -name "index.en.md" -o -name "index.zh.md" | head -1)
    [ -z "$has_child_content" ] && echo "ORPHAN: $dir"
  fi
done
```

**Checklist:**
- [ ] Every content directory has both `index.en.md` and `index.zh.md`
- [ ] Every content file has `title` in frontmatter
- [ ] Every content file has `weight` in frontmatter
- [ ] Weight values are numeric and create correct ordering
- [ ] No orphan directories exist
- [ ] EN and ZH files have matching `weight` values

### Phase 2: Bilingual Consistency

Compare EN/ZH file pairs for structural parity.

**2a. Compare heading counts:**

```bash
for en_file in $(find "$CONTENT_DIR" -name "index.en.md" | sort); do
  zh_file="${en_file%.en.md}.zh.md"
  [ -f "$zh_file" ] || continue

  en_headings=$(grep -c "^#" "$en_file")
  zh_headings=$(grep -c "^#" "$zh_file")

  dir=$(dirname "$en_file" | sed "s|$CONTENT_DIR/||")
  echo "$dir | Headings: EN=$en_headings ZH=$zh_headings"
done
```

**2b. Compare image reference counts:**

```bash
for en_file in $(find "$CONTENT_DIR" -name "index.en.md" | sort); do
  zh_file="${en_file%.en.md}.zh.md"
  [ -f "$zh_file" ] || continue

  en_images=$(grep -co '!\[' "$en_file")
  zh_images=$(grep -co '!\[' "$zh_file")

  # Also compare actual image paths
  en_paths=$(grep -oP '!\[[^\]]*\]\(\K[^)]+' "$en_file" | sort)
  zh_paths=$(grep -oP '!\[[^\]]*\]\(\K[^)]+' "$zh_file" | sort)

  dir=$(dirname "$en_file" | sed "s|$CONTENT_DIR/||")
  if [ "$en_paths" != "$zh_paths" ]; then
    echo "MISMATCH $dir | Images: EN=$en_images ZH=$zh_images (different paths)"
  else
    echo "OK $dir | Images: EN=$en_images ZH=$zh_images"
  fi
done
```

**2c. Compare alert counts and types:**

```bash
for en_file in $(find "$CONTENT_DIR" -name "index.en.md" | sort); do
  zh_file="${en_file%.en.md}.zh.md"
  [ -f "$zh_file" ] || continue

  en_alerts=$(grep -c '::::alert' "$en_file")
  zh_alerts=$(grep -c '::::alert' "$zh_file")

  # Compare alert types
  en_types=$(grep -oP '::::alert\{type="\K[^"]+' "$en_file" | sort)
  zh_types=$(grep -oP '::::alert\{type="\K[^"]+' "$zh_file" | sort)

  dir=$(dirname "$en_file" | sed "s|$CONTENT_DIR/||")
  echo "$dir | Alerts: EN=$en_alerts ZH=$zh_alerts | Types match: $([ "$en_types" = "$zh_types" ] && echo yes || echo NO)"
done
```

**2d. Compare code block counts:**

```bash
for en_file in $(find "$CONTENT_DIR" -name "index.en.md" | sort); do
  zh_file="${en_file%.en.md}.zh.md"
  [ -f "$zh_file" ] || continue

  en_code=$(grep -c '```' "$en_file")
  zh_code=$(grep -c '```' "$zh_file")

  dir=$(dirname "$en_file" | sed "s|$CONTENT_DIR/||")
  echo "$dir | Code fences: EN=$en_code ZH=$zh_code"
done
```

**2e. Check for missing translations (one language exists but not the other):**

```bash
# EN exists but no ZH
for f in $(find "$CONTENT_DIR" -name "index.en.md" | sort); do
  zh="${f%.en.md}.zh.md"
  [ ! -f "$zh" ] && echo "MISSING ZH: $f"
done

# ZH exists but no EN
for f in $(find "$CONTENT_DIR" -name "index.zh.md" | sort); do
  en="${f%.zh.md}.en.md"
  [ ! -f "$en" ] && echo "MISSING EN: $f"
done
```

**Checklist:**
- [ ] Heading counts match between EN and ZH
- [ ] Image references are identical between EN and ZH
- [ ] Alert counts and types match
- [ ] Code block counts match (code should be identical, only surrounding text translated)
- [ ] No missing translations (every EN has a ZH, every ZH has an EN)

### Phase 3: Asset Hygiene

Audit images and static assets.

**3a. List all images referenced in content files:**

```bash
# Extract all image paths from markdown files
grep -rhoP '!\[[^\]]*\]\(\K[^)]+' "$CONTENT_DIR" | sort -u > /tmp/ws-review-referenced-images.txt
cat /tmp/ws-review-referenced-images.txt
```

**3b. List all images on disk:**

```bash
# List all image files in static/images/
find "$WORKSHOP_DIR/static/images" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.gif" -o -iname "*.svg" -o -iname "*.webp" \) 2>/dev/null | sort > /tmp/ws-review-disk-images.txt
cat /tmp/ws-review-disk-images.txt
```

**3c. Find unused images (on disk but not referenced):**

```bash
while IFS= read -r img_path; do
  # Convert absolute path to /static/images/... reference format
  ref="/static/images/$(basename "$img_path")"
  # Also check with subdirectory paths
  ref_full=$(echo "$img_path" | sed "s|$WORKSHOP_DIR||")
  if ! grep -qF "$ref" /tmp/ws-review-referenced-images.txt && \
     ! grep -qF "$ref_full" /tmp/ws-review-referenced-images.txt && \
     ! grep -qF "$(basename "$img_path")" /tmp/ws-review-referenced-images.txt; then
    echo "UNUSED: $img_path"
  fi
done < /tmp/ws-review-disk-images.txt
```

**3d. Find broken references (referenced but file not on disk):**

```bash
while IFS= read -r ref; do
  # Only check /static/ references (not external URLs)
  case "$ref" in
    /static/*)
      full_path="$WORKSHOP_DIR$ref"
      [ ! -f "$full_path" ] && echo "BROKEN: $ref"
      ;;
  esac
done < /tmp/ws-review-referenced-images.txt
```

**3e. Check for debug/temporary images:**

```bash
find "$WORKSHOP_DIR/static/images" -type f \( \
  -name "debug-*" -o -name "test-*" -o -name "tmp-*" -o \
  -name "temp-*" -o -name "screenshot-*" -o -name "Screen Shot*" -o \
  -name "Screenshot*" -o -name "Untitled*" \
\) 2>/dev/null
```

**3f. Check image file sizes (warn if > 500KB):**

```bash
find "$WORKSHOP_DIR/static/images" -type f -size +500k \( \
  -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.gif" -o -iname "*.svg" -o -iname "*.webp" \
\) -exec ls -lh {} \; 2>/dev/null | awk '{print $5, $NF}'
```

**Checklist:**
- [ ] No broken image references
- [ ] No unused images cluttering static/
- [ ] No debug/temporary images
- [ ] No oversized images (>500KB)
- [ ] Image naming follows convention (lowercase, hyphens, descriptive)

### Phase 4: Link Integrity

Validate internal and external links.

**4a. Check internal cross-references (relative links):**

```bash
# Extract all markdown links (not images) from content files
grep -rhoP '\[[^\]]+\]\(\K[^)]+' "$CONTENT_DIR" | grep -v '^!' | grep -v '^http' | grep -v '^#' | sort -u > /tmp/ws-review-internal-links.txt

# For each relative link, check if target directory exists
while IFS= read -r link; do
  # Skip asset URLs and anchors
  case "$link" in
    :assetUrl*|#*|http*|mailto*) continue ;;
  esac
  echo "LINK: $link"
done < /tmp/ws-review-internal-links.txt
```

**4b. Validate relative links resolve to existing directories:**

```bash
# For each content file, check its relative links
for f in $(find "$CONTENT_DIR" -name "index.en.md" | sort); do
  dir=$(dirname "$f")
  links=$(grep -oP '\[[^\]]+\]\(\K[^)]+' "$f" | grep -v '^http' | grep -v '^#' | grep -v ':assetUrl')
  for link in $links; do
    # Remove any anchor fragment
    target="${link%%#*}"
    [ -z "$target" ] && continue
    # Resolve relative path
    resolved="$dir/$target"
    if [ ! -d "$resolved" ] && [ ! -f "$resolved" ] && [ ! -d "$(realpath "$resolved" 2>/dev/null)" ]; then
      # Also check if it's an absolute path from content root
      case "$target" in
        /*) resolved="$WORKSHOP_DIR$target"
            [ ! -d "$resolved" ] && [ ! -f "$resolved" ] && echo "BROKEN LINK: $f -> $link"
            ;;
        *)  echo "BROKEN LINK: $f -> $link" ;;
      esac
    fi
  done
done
```

**4c. Check `:assetUrl` directive usage:**

```bash
# Find all :assetUrl references
grep -rn ':assetUrl' "$CONTENT_DIR" | while IFS= read -r line; do
  echo "$line"
  # Verify format: :assetUrl{path="..." source=s3} or :assetUrl{path="..."}
  echo "$line" | grep -qP ':assetUrl\{path="[^"]+"\s*(source=(s3|repo))?\}' || echo "  ^ INVALID FORMAT"
done
```

**4d. Check for hardcoded Workshop Studio URLs that should be relative:**

```bash
# Find hardcoded workshop studio URLs
grep -rn 'catalog.workshops.aws\|catalog.us-east-1.prod.workshops.aws\|studio.us-east-1.prod.workshops.aws' "$CONTENT_DIR" 2>/dev/null
```

**4e. Check for /assets/ links (common mistake - these 404 on published workshops):**

```bash
# Standard markdown links to /assets/ will 404
grep -rn '\](/assets/' "$CONTENT_DIR" 2>/dev/null | grep -v ':assetUrl'
```

**Checklist:**
- [ ] All relative links resolve to existing directories/files
- [ ] `:assetUrl` directives use correct syntax
- [ ] No hardcoded Workshop Studio URLs
- [ ] No direct `/assets/` markdown links (these 404 on published workshops)
- [ ] External URLs use proper format (https://)

### Phase 5: Content Quality

Check content for completeness and correctness.

**5a. Find TODO/FIXME/PLACEHOLDER/TBD markers:**

```bash
grep -rn 'TODO\|FIXME\|PLACEHOLDER\|TBD\|HACK\|XXX\|TEMP' "$CONTENT_DIR" --include="*.md" 2>/dev/null
```

**5b. Check for empty sections (heading followed immediately by another heading):**

```bash
for f in $(find "$CONTENT_DIR" -name "*.md" | sort); do
  # Find consecutive heading lines (allowing blank lines between)
  awk '
    /^#{1,6} / { 
      if (prev_heading && !has_content) {
        print FILENAME ":" prev_line ": Empty section: " prev_heading
      }
      prev_heading = $0
      prev_line = NR
      has_content = 0
      next
    }
    /^[[:space:]]*$/ { next }
    { has_content = 1 }
  ' "$f"
done
```

**5c. Verify alert syntax is correct (four colons, valid type):**

```bash
# Find alert blocks and validate syntax
grep -rn ':::' "$CONTENT_DIR" --include="*.md" | while IFS= read -r line; do
  # Check for three-colon alerts (should be four in content, three in facilitator guide)
  echo "$line" | grep -qP ':::alert' && ! echo "$line" | grep -qP '::::alert' && echo "WRONG COLONS: $line"
  
  # Check for valid alert types
  echo "$line" | grep -qP '::::alert\{type="' && \
    ! echo "$line" | grep -qP '::::alert\{type="(info|warning|success|error|tip)"' && \
    echo "INVALID ALERT TYPE: $line"
done

# Check for unclosed alert blocks
for f in $(find "$CONTENT_DIR" -name "*.md" | sort); do
  open=$(grep -c '::::alert{' "$f")
  close=$(grep -c '^::::$' "$f")
  [ "$open" -ne "$close" ] && echo "UNCLOSED ALERTS in $f: opened=$open closed=$close"
done
```

**5d. Check AWS service name casing:**

```bash
# Common misspellings/miscasing of AWS service names
grep -rnP '(?i)\b(amazon q|quicksight|bedrock|sagemaker|dynamodb|cloudwatch|cloudfront|cloudformation)\b' "$CONTENT_DIR" --include="*.md" | \
  grep -vP '\b(Amazon Q|QuickSight|Bedrock|SageMaker|DynamoDB|CloudWatch|CloudFront|CloudFormation)\b' | \
  grep -vP '```' | \
  grep -vP '^\s*#' 2>/dev/null
```

**5e. Verify code blocks have language specifiers:**

```bash
# Find code blocks without language specifiers
for f in $(find "$CONTENT_DIR" -name "*.md" | sort); do
  grep -n '^```$' "$f" | while IFS=: read -r line_num _; do
    # Check if this is an opening or closing fence
    # Count fences before this line; if odd, this is a closing fence (OK)
    before=$(head -n "$((line_num - 1))" "$f" | grep -c '^```')
    if [ $((before % 2)) -eq 0 ]; then
      echo "NO LANG SPEC: $f:$line_num"
    fi
  done
done
```

**5f. Check for broken markdown tables:**

```bash
# Find tables with inconsistent column counts
for f in $(find "$CONTENT_DIR" -name "*.md" | sort); do
  awk '
    /^\|/ {
      cols = gsub(/\|/, "|") - 1
      if (table_cols == 0) { table_cols = cols; table_start = NR }
      else if (cols != table_cols) {
        print FILENAME ":" NR ": Table column mismatch (expected " table_cols " got " cols ")"
      }
      in_table = 1
      next
    }
    in_table { in_table = 0; table_cols = 0 }
  ' "$f"
done
```

**Checklist:**
- [ ] No TODO/FIXME/PLACEHOLDER/TBD markers remain
- [ ] No empty sections (heading with no content before next heading)
- [ ] Alert blocks use `::::` (four colons) with valid types
- [ ] Alert blocks are properly closed
- [ ] AWS service names use correct casing
- [ ] Code blocks have language specifiers
- [ ] Markdown tables have consistent column counts

### Phase 6: Navigation Flow

Verify the workshop navigation creates a logical progression.

**6a. Verify weight ordering creates logical progression:**

```bash
# Build a tree of weights
for f in $(find "$CONTENT_DIR" -name "index.en.md" | sort); do
  dir=$(dirname "$f" | sed "s|$CONTENT_DIR||")
  weight=$(sed -n '/^---$/,/^---$/{ s/^weight: *//p }' "$f")
  title=$(sed -n '/^---$/,/^---$/{ s/^title: *"*//; s/"*$//p }' "$f")
  depth=$(echo "$dir" | tr -cd '/' | wc -c)
  echo "W=$weight D=$depth $dir | $title"
done | sort -t= -k2 -n
```

**6b. Check "Next" / "Continue" links at bottom of pages:**

```bash
for f in $(find "$CONTENT_DIR" -name "index.en.md" | sort); do
  dir=$(dirname "$f")
  # Look for navigation links in last 10 lines
  next_links=$(tail -10 "$f" | grep -oP '\[[^\]]*(?:Next|Continue|Start|next|continue|start)[^\]]*\]\([^)]+\)')
  if [ -n "$next_links" ]; then
    echo "$(dirname "$f" | sed "s|$CONTENT_DIR/||"): $next_links"
    # Verify the target exists
    target=$(echo "$next_links" | grep -oP '\(\K[^)]+' | head -1)
    case "$target" in
      http*|#*|:*) ;; # skip external/anchor/asset links
      *)
        resolved="$dir/$target"
        [ ! -d "$resolved" ] && echo "  BROKEN NEXT: $target"
        ;;
    esac
  fi
done
```

**6c. Verify lab numbering is sequential:**

```bash
# Check that directories like 01-*, 02-*, 03-* are sequential within each parent
for parent in $(find "$CONTENT_DIR" -type d | sort); do
  nums=$(ls -d "$parent"/[0-9]*/ 2>/dev/null | sed 's|.*/\([0-9]*\)-.*|\1|' | sort -n)
  [ -z "$nums" ] && continue
  prev=""
  for n in $nums; do
    n_int=$((10#$n))
    if [ -n "$prev" ]; then
      gap=$((n_int - prev))
      # Gaps are OK (10, 20, 30 pattern) but flag if a number is out of sequence
      if [ $n_int -le $prev ]; then
        echo "OUT OF ORDER in $parent: $n_int <= $prev"
      fi
    fi
    prev=$n_int
  done
done
```

**6d. Verify weight values within same parent don't collide:**

```bash
for parent in $(find "$CONTENT_DIR" -type d | sort); do
  weights=""
  for child in "$parent"/*/index.en.md; do
    [ -f "$child" ] || continue
    w=$(sed -n '/^---$/,/^---$/{ s/^weight: *//p }' "$child")
    [ -n "$w" ] && weights="$weights $w"
  done
  dupes=$(echo $weights | tr ' ' '\n' | sort | uniq -d)
  [ -n "$dupes" ] && echo "DUPLICATE WEIGHTS in $parent: $dupes"
done
```

**Checklist:**
- [ ] Weight values create a logical progression (lower weights appear first)
- [ ] No duplicate weights among siblings
- [ ] "Next"/"Continue" links point to correct subsequent sections
- [ ] Lab directories are numbered sequentially
- [ ] No weight collisions within the same parent

### Phase 7: Review Report

After running all phases, compile findings into a structured report.

**Report format:**

```markdown
## Workshop Review Report

### Workshop: [title from content/index.en.md frontmatter]
### Path: [absolute path to workshop directory]
### Date: [current date]
### Verdict: PASS / PASS WITH WARNINGS / FAIL

---

### 1. Structure & Frontmatter

| Directory | EN | ZH | Weight | Status |
|-----------|----|----|--------|--------|
| content/ | OK | OK | - | PASS |
| 10-lab-1/ | OK | OK | 20 | PASS |
| 10-lab-1/01-step/ | OK | MISSING | 21 | CRITICAL |

**Issues:**
- CRITICAL: [directory] missing index.zh.md
- WARNING: [directory] has no weight in frontmatter

---

### 2. Bilingual Consistency

| File Pair | Headings | Images | Alerts | Code Blocks | Status |
|-----------|----------|--------|--------|-------------|--------|
| 10-lab-1/ | 5/5 | 3/3 | 2/2 | 4/4 | PASS |
| 20-lab-2/ | 5/4 | 3/2 | 2/2 | 4/4 | WARNING |

**Mismatches:**
- WARNING: 20-lab-2/ has 5 EN headings but 4 ZH headings
- CRITICAL: 20-lab-2/ has different image references in EN vs ZH

---

### 3. Asset Hygiene

- **Referenced images**: N
- **Images on disk**: M
- **Unused images**: K
- **Broken references**: J
- **Oversized images (>500KB)**: L
- **Debug/temp images**: 0

**Unused images:**
- WARNING: /static/images/old-screenshot.png

**Broken references:**
- CRITICAL: /static/images/missing-diagram.png (referenced in 10-lab-1/index.en.md)

**Oversized images:**
- WARNING: /static/images/full-page-capture.png (1.2MB)

---

### 4. Link Integrity

| Link | Source File | Target | Status |
|------|-----------|--------|--------|
| ../02-step | 10-lab-1/01-step/ | 10-lab-1/02-step/ | PASS |
| ../missing | 20-lab-2/01-step/ | 20-lab-2/missing/ | CRITICAL |

**Issues:**
- CRITICAL: Broken relative link ../missing in 20-lab-2/01-step/index.en.md
- CRITICAL: Direct /assets/ link found (will 404 on published workshop)
- WARNING: Hardcoded Workshop Studio URL found

---

### 5. Content Quality

| Check | Count | Status |
|-------|-------|--------|
| TODOs/FIXMEs | 0 | PASS |
| Empty sections | 1 | WARNING |
| Alert syntax errors | 0 | PASS |
| Service name casing | 2 | WARNING |
| Code blocks without lang | 3 | WARNING |
| Broken tables | 0 | PASS |

**Issues:**
- WARNING: Empty section at 10-lab-1/index.en.md:42
- WARNING: "Amazon q" should be "Amazon Q" at 20-lab-2/index.en.md:15
- WARNING: Code block without language specifier at 10-lab-1/index.en.md:88

---

### 6. Navigation Flow

| Check | Status | Details |
|-------|--------|---------|
| Weight ordering | PASS | All weights create logical progression |
| Duplicate weights | PASS | No collisions |
| Next/Continue links | WARNING | 1 broken next link |
| Lab numbering | PASS | Sequential |

**Issues:**
- WARNING: Broken "Next" link in 20-lab-2/03-step/index.en.md pointing to ../04-step (does not exist)

---

### Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 2 |
| WARNING | 8 |
| SUGGESTION | 3 |

**Must fix (CRITICAL):**
1. Missing index.zh.md in 10-lab-1/01-step/
2. Broken image reference /static/images/missing-diagram.png

**Should fix (WARNING):**
1. Heading count mismatch in 20-lab-2/ (EN=5, ZH=4)
2. Unused image old-screenshot.png
3. AWS service name "Amazon q" should be "Amazon Q"
4. 3 code blocks without language specifiers

**Nice to have (SUGGESTION):**
1. Consider compressing full-page-capture.png (1.2MB)
2. Add alt text to images where missing
```

## Auto-Fix Mode (--fix)

When `--fix` is passed, automatically fix these simple issues:

**Fixable issues:**
1. **Missing code block language specifiers**: Add `text` as default language
2. **AWS service name casing**: Fix common misspellings (Amazon q -> Amazon Q, Quicksight -> QuickSight, etc.)
3. **Trailing whitespace**: Remove from all markdown files
4. **Unclosed alert blocks**: Add closing `::::` if clearly missing

**NOT auto-fixed (require human judgment):**
- Missing translations
- Broken links
- Content structure changes
- Image issues
- Navigation flow

```bash
# Example: Fix code blocks without language specifiers
for f in $(find "$CONTENT_DIR" -name "*.md"); do
  # Add 'text' to bare ``` opening fences
  # (careful: only opening fences, not closing ones)
  # This requires context-aware replacement - do it carefully per file
  echo "Would fix: $f"
done

# Example: Fix service name casing
for f in $(find "$CONTENT_DIR" -name "*.md"); do
  sed -i 's/\bAmazon q\b/Amazon Q/g' "$f"
  sed -i 's/\bQuicksight\b/QuickSight/g' "$f"
  sed -i 's/\bSagemaker\b/SageMaker/g' "$f"
  sed -i 's/\bDynamodb\b/DynamoDB/g' "$f"
  sed -i 's/\bCloudwatch\b/CloudWatch/g' "$f"
  sed -i 's/\bCloudfront\b/CloudFront/g' "$f"
  sed -i 's/\bCloudformation\b/CloudFormation/g' "$f"
done
```

## Severity Levels

- **CRITICAL**: Broken references, missing translations, broken navigation, invalid alert syntax, direct /assets/ links. These WILL cause visible problems for workshop participants.
- **WARNING**: Unused assets, inconsistent naming, missing code language specifiers, heading count mismatches, oversized images. These degrade quality but don't break the workshop.
- **SUGGESTION**: Style improvements, image compression opportunities, minor naming inconsistencies. Nice to have but not blocking.

## Verdict Criteria

- **PASS**: No CRITICAL or WARNING issues
- **PASS WITH WARNINGS**: No CRITICAL issues, but has WARNING-level issues
- **FAIL**: Has one or more CRITICAL issues

## Integration with Publishing Workflow

Typical workflow:

```
1. Write/update workshop content
2. /workshop-review                    # Audit everything
3. Fix CRITICAL and WARNING issues
4. /workshop-review                    # Re-audit
5. git add -A && git commit            # Commit when review passes
6. git push                            # Publish to Workshop Studio
```

## Notes

- This skill is self-contained: all checks use standard Unix tools (find, grep, awk, sed)
- No external dependencies required
- The workshop directory defaults to current directory but can be passed as an argument
- For bilingual workshops, the skill checks both EN and ZH; for EN-only workshops, bilingual checks are skipped
- Always run this skill from the workshop root directory or pass the full path
- The `contentspec.yaml` file at the workshop root is used to determine declared languages
