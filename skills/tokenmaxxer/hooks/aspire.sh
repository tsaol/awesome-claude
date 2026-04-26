#!/bin/bash
# Tokenmaxxer: Aspiration injection before processing user requests
# Hook type: UserPromptSubmit

INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')

# Only inject on substantive prompts, not short confirmations
if [ ${#PROMPT} -gt 15 ]; then
  cat <<EOF
{
  "hookSpecificOutput": {
    "additionalContext": "Aspiration: Approach this with depth. If you write code, also consider tests. If you fix a bug, look for the pattern. If you can parallelize with subagents, do it. Aim for excellent, not just done."
  }
}
EOF
fi

exit 0
