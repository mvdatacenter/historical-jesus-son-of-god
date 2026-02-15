#!/bin/bash
# PreToolUse guard for destructive bash commands.
# Blocks commands that are almost always symptoms of treating the wrong problem.
#
# DESIGN RULES — read before adding new entries:
#
# 1. Every entry must ALWAYS indicate a mistake. Not "usually bad" or
#    "sometimes hacky" — ALWAYS. If there is any legitimate reason for
#    Claude to run the command during normal engineering work, it does
#    not belong here. "kill" qualifies because Claude killing processes
#    always means Claude is covering up a root cause. "sleep" does NOT
#    qualify because sleep is a normal command with many legitimate uses.
#
# 2. Never parse bash syntax with regex. You cannot reliably detect
#    shell operators (&&, ||, ;, |) because they appear inside strings,
#    heredocs, jq expressions, URLs, and other non-operator contexts.
#    A naive regex will false-positive constantly and break the guard.
#
# 3. Small and precise beats comprehensive and wrong. Two rules that
#    are always right are worth more than ten that sometimes false-positive.
#    A bad rule in this guard breaks every repo in the org.
#
# 4. Test every new rule before committing. Pipe sample commands through
#    the script and verify both true positives and false negatives.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "default"')
CHALLENGE_FILE=".claude/.guard-challenge-$SESSION_ID"

# Guarded blocks — require one-time challenge passphrase
if echo "$COMMAND" | grep -qE 'git\s.*push\s.*(-f\b|--force)'; then
    EXPECTED=$(cat "$CHALLENGE_FILE" 2>/dev/null)
    if [ -n "$EXPECTED" ] && echo "$COMMAND" | grep -q "^BYPASS=$EXPECTED "; then
        rm -f "$CHALLENGE_FILE"
        exit 0
    fi
    CHALLENGE=$((RANDOM % 9000 + 1000))
    echo "$CHALLENGE" > "$CHALLENGE_FILE"
    echo "BLOCKED: Read CLAUDE.md." >&2
    exit 2
fi

if echo "$COMMAND" | grep -qE '(^|\s)(kill|pkill|killall)\s'; then
    EXPECTED=$(cat "$CHALLENGE_FILE" 2>/dev/null)
    if [ -n "$EXPECTED" ] && echo "$COMMAND" | grep -q "^BYPASS=$EXPECTED "; then
        rm -f "$CHALLENGE_FILE"
        exit 0
    fi
    CHALLENGE=$((RANDOM % 9000 + 1000))
    echo "$CHALLENGE" > "$CHALLENGE_FILE"
    echo "BLOCKED: Read CLAUDE.md." >&2
    exit 2
fi

exit 0
