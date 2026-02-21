#!/bin/bash
# PreToolUse guard for kill commands.
#
# kill is a shell builtin so PATH wrappers can't intercept it.
# This hook inspects the Bash tool input before execution.
# Force push is caught by the git wrapper.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "default"')
CHALLENGE_FILE=".claude/.guard-challenge-$SESSION_ID"

if echo "$COMMAND" | grep -qE '^kill\s'; then
    EXPECTED=$(cat "$CHALLENGE_FILE" 2>/dev/null)
    if [ -n "$EXPECTED" ] && echo "$COMMAND" | grep -q "^BYPASS=$EXPECTED "; then
        rm -f "$CHALLENGE_FILE"
        exit 0
    fi
    CHALLENGE=$((RANDOM % 9000 + 1000))
    echo "$CHALLENGE" > "$CHALLENGE_FILE"
    echo "BLOCKED: kill is almost always wrong. Read CLAUDE.md." >&2
    echo "If genuinely needed, read passphrase from $CHALLENGE_FILE and prefix with BYPASS=<passphrase>" >&2
    exit 2
fi

exit 0
