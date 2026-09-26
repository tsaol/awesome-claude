#!/bin/bash
# Tokenmaxxer: Self-reflection injection after meaningful code actions
# Hook type: PostToolUse (matcher: Edit|Write|Bash)

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

emit() {
  jq -n --arg ctx "$1" '{
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: $ctx
    }
  }'
}

# Command boundary: start of string or after ; & | or whitespace
B='(^|[;&|[:space:]])'
# End of a command word
E='([;&|[:space:]]|$)'
# git, optionally followed by global options (e.g. -C dir, -c k=v, --no-pager), then commit
GIT_COMMIT_RE="${B}git([[:space:]]+-[^[:space:]]+([[:space:]]+[^-[:space:]][^[:space:]]*)?)*[[:space:]]+commit${E}"
TEST_RE="${B}(pytest|npm test|go test|cargo test|make test)${E}"

case "$TOOL_NAME" in
  Edit|Write)
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
    if echo "$FILE_PATH" | grep -qE '\.(py|ts|tsx|js|jsx|go|rs|java|rb|kt|swift|c|cpp|h)$'; then
      emit "Self-reflect: You just modified ${FILE_PATH}. Does this change have test coverage? Did you handle edge cases? Could this introduce a regression? If something is missing, address it now before moving on."
    fi
    ;;
  Bash)
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
    if echo "$COMMAND" | grep -qE "$GIT_COMMIT_RE"; then
      emit "Self-reflect: You just committed code. Did you commit everything that belongs together? Are there related improvements you noticed but haven't addressed? Is there a test you meant to add?"
    elif echo "$COMMAND" | grep -qE "$TEST_RE"; then
      emit "Self-reflect: You just ran tests. If any failed, investigate the root cause — don't just fix the symptom. If all passed, consider: are there edge cases not covered by existing tests?"
    fi
    ;;
esac

exit 0
