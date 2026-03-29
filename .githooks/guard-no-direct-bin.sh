#!/bin/bash
# Blocks direct calls to /usr/bin/git and /usr/bin/gh, forcing all
# commands through the guard wrappers at ~/.local/bin/.
# Without this, the AI can bypass every guard by calling the real binary.
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if echo "$COMMAND" | grep -qE '/usr/bin/git\b|/usr/local/bin/git\b|/opt/homebrew/bin/git\b'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "BLOCKED: Direct path to git binary bypasses guard wrappers. Use git (not /usr/bin/git)."
    }
  }'
  exit 0
fi

if echo "$COMMAND" | grep -qE '/usr/bin/gh\b|/usr/local/bin/gh\b|/opt/homebrew/bin/gh\b'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "BLOCKED: Direct path to gh binary bypasses guard wrappers. Use gh (not /usr/bin/gh)."
    }
  }'
  exit 0
fi

exit 0
