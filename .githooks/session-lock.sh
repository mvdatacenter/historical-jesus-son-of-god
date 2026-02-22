#!/bin/bash
# Thin wrapper. Runs session-lock.sh from .claude-shared/ cache.

SCRIPT=".claude-shared/session-lock.sh"
RAW="https://raw.githubusercontent.com/mvdatacenter/claude-instructions/main/hooks/session-lock.sh"

if [ ! -f "$SCRIPT" ]; then
    mkdir -p .claude-shared
    TOKEN=$(gh auth token 2>/dev/null)
    curl -sf -H "Authorization: token $TOKEN" "$RAW" -o "$SCRIPT"
fi

[ -f "$SCRIPT" ] && bash "$SCRIPT"
