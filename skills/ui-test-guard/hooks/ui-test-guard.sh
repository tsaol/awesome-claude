#!/bin/bash
# ui-test-guard: Stop hook that warns Claude when it claims a UI change is
# done/deployed/verified without showing evidence that a real-browser UI
# test passed.
#
# Triggers when the last assistant turn contains BOTH:
#   - a "claim" word (deployed, verified, done, shipped, live, tested, complete, works),
#     matched as a whole word ("incomplete" does not count as "complete")
#   - a real URL (http:// or https://, or localhost / 127.0.0.1 with a port)
# AND does NOT contain UI-test evidence (ALL PASSED, ui-test, run_tests.py).
#
# Configure the regexes below for your project. The default URL regex only
# matches real URLs, not filesystem paths like /home/user/app.
#
# Behavior:
#   - exit 0 = pass silently
#   - exit 2 = block the stop; stderr is fed back to Claude, which keeps going
#   - if stop_hook_active is true (Claude is already continuing because of a
#     Stop hook), exit 0 so the guard can never loop forever
#
# Failure modes are fail-open: if jq is missing, transcript is unreadable,
# or anything else goes wrong, exit 0 (no false positives blocking work).

set -euo pipefail

INPUT=$(cat)

# Already continuing because of a Stop hook -> never block again (no loops).
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null || echo "")
[ "$STOP_ACTIVE" = "true" ] && exit 0

TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // empty' 2>/dev/null || echo "")
[ -z "$TRANSCRIPT" ] && exit 0
[ ! -r "$TRANSCRIPT" ] && exit 0

# Pull the most recent assistant message text out of the JSONL transcript.
LAST_ASSISTANT=$(tac "$TRANSCRIPT" 2>/dev/null \
  | jq -rs '
      [.[] | select(.type == "assistant")][0]
      | .message.content
      | if type == "array" then [.[] | select(.type=="text") | .text] | join("\n")
        else (. // "") end
    ' 2>/dev/null || echo "")

[ -z "$LAST_ASSISTANT" ] && exit 0

# Optional debug log, opt-in via UI_TEST_GUARD_DEBUG=1
LOG="${UI_TEST_GUARD_LOG:-/tmp/ui-test-guard.log}"
log() {
  [ "${UI_TEST_GUARD_DEBUG:-0}" = "1" ] || return 0
  echo "$(date '+%F %T') | $1" >> "$LOG" 2>/dev/null || true
}
log "guard fired | len=${#LAST_ASSISTANT}"

# === Regex configuration ===
# CLAIM_RE: words that suggest the agent is reporting a UI change as complete
#           (matched with grep -w, so each alternative must be a whole word)
# URL_RE:   patterns that suggest the change touches a real web surface
# EVIDENCE_RE: patterns that prove a real-browser test was run and passed
#
# Override any of these via env vars before the hook runs, e.g. in
# settings.json -> hooks -> Stop -> command, prefix the path with
# `env UI_TEST_GUARD_URL_RE=... ` or wrap in another script.

CLAIM_RE="${UI_TEST_GUARD_CLAIM_RE:-(deployed|verified|shipped|live|tested|complete|works|all[[:space:]]passed|done)}"
URL_RE="${UI_TEST_GUARD_URL_RE:-(https?://[a-zA-Z0-9.-]+|(localhost|127\.0\.0\.1):[0-9]+)}"
EVIDENCE_RE="${UI_TEST_GUARD_EVIDENCE_RE:-(ui-test|run_tests\.py|ALL[[:space:]]PASSED|playwright|cypress|build_tests\.py)}"

if echo "$LAST_ASSISTANT" | grep -qiwE "$CLAIM_RE" \
   && echo "$LAST_ASSISTANT" | grep -qiE "$URL_RE" \
   && ! echo "$LAST_ASSISTANT" | grep -qiE "$EVIDENCE_RE"; then

  REMINDER='UI-TEST GUARD: Your last reply claims a UI change is done/deployed/verified for a web surface, but contains no evidence that a real-browser UI test passed (no "ui-test", "run_tests.py", "ALL PASSED", "playwright", or "cypress" mention).

Curl + grep does NOT count as end-to-end testing for UI changes. Curl can only confirm the HTML contains a string; it cannot catch CSS layout breakage, hydration errors, RSC payload leaks, blank screens, or visual regressions.

Before continuing:
  1. Run your real-browser UI test suite against the deployed change.
  2. Report the actual pass/fail count to the user.
  3. If you already ran the test but did not mention it, say so explicitly in your next reply.'

  log "TRIGGERED"
  echo "$REMINDER" >&2
  exit 2
fi

exit 0
