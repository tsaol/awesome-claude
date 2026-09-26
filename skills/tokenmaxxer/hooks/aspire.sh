#!/bin/bash
# Tokenmaxxer: Aspiration injection before processing user requests
# Hook type: UserPromptSubmit

INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')

# Skip slash commands
case "$PROMPT" in
  /*) exit 0 ;;
esac

# Only inject on substantive prompts, not short confirmations
if [ ${#PROMPT} -gt 15 ]; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      additionalContext: "Aspiration: Approach this with depth. If you write code, also consider tests. If you fix a bug, look for the pattern. If you can parallelize with subagents, do it. Aim for excellent, not just done."
    }
  }'
fi

exit 0
