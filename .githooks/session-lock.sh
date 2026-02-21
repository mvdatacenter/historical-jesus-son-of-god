#!/bin/bash
# PreToolUse guard: prevents concurrent repo edits by different Claude sessions.
#
# Acquires a session lock on first write tool call (Edit, Write, NotebookEdit).
# Blocks other sessions while the owning session is alive and active.
# Lock is stale if owning PID is dead OR timestamp > 10 minutes old.
#
# Non-write tools (Bash, Read, etc.) don't acquire or block, but if the
# calling session already owns the lock, any tool call refreshes the heartbeat.
# This keeps the lock alive during post-edit phases (PR review, merge commands)
# where the session is still active but not calling write tools.

LOCK_FILE=".claude/.session-lock"

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "default"')
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

mkdir -p .claude

NOW=$(date +%s)
STALE_SECONDS=600  # 10 minutes

acquire_lock() {
    jq -n --arg sid "$SESSION_ID" --arg pid "$PPID" --arg ts "$NOW" \
        '{"session_id": $sid, "pid": ($pid | tonumber), "timestamp": ($ts | tonumber)}' \
        > "$LOCK_FILE"
}

# Determine if this is a write tool (acquires + blocks) or other (heartbeat only)
IS_WRITE=0
case "$TOOL_NAME" in
    Edit|Write|NotebookEdit) IS_WRITE=1 ;;
esac

# Non-write tool: only refresh heartbeat if we already own the lock, then exit
if [ "$IS_WRITE" -eq 0 ]; then
    if [ -f "$LOCK_FILE" ]; then
        LOCK_SESSION=$(jq -r '.session_id // empty' "$LOCK_FILE" 2>/dev/null)
        if [ "$LOCK_SESSION" = "$SESSION_ID" ]; then
            acquire_lock
        fi
    fi
    exit 0
fi

# --- Write tool path: acquire, refresh, or block ---

# No lock file → acquire
if [ ! -f "$LOCK_FILE" ]; then
    acquire_lock
    exit 0
fi

# Read existing lock
LOCK_SESSION=$(jq -r '.session_id // empty' "$LOCK_FILE" 2>/dev/null)
LOCK_PID=$(jq -r '.pid // empty' "$LOCK_FILE" 2>/dev/null)
LOCK_TS=$(jq -r '.timestamp // empty' "$LOCK_FILE" 2>/dev/null)

# Corrupt or empty lock → take over
if [ -z "$LOCK_SESSION" ] || [ -z "$LOCK_PID" ] || [ -z "$LOCK_TS" ]; then
    acquire_lock
    exit 0
fi

# Same session → refresh heartbeat
if [ "$LOCK_SESSION" = "$SESSION_ID" ]; then
    acquire_lock
    exit 0
fi

# Different session — check staleness

# PID dead?
if ! kill -0 "$LOCK_PID" 2>/dev/null; then
    acquire_lock
    exit 0
fi

# Timestamp too old?
AGE=$((NOW - LOCK_TS))
if [ "$AGE" -gt "$STALE_SECONDS" ]; then
    acquire_lock
    exit 0
fi

# Active lock held by another session → block
echo "BLOCKED: Another Claude session ($LOCK_SESSION, PID $LOCK_PID) is actively editing this repo." >&2
echo "Lock acquired ${AGE}s ago. If the other session is gone, remove the lock:" >&2
echo "  rm $LOCK_FILE" >&2
exit 2
