#!/bin/bash
# Thin wrapper. Runs guard-destructive.sh from .claude-shared/ cache.

SCRIPT=".claude-shared/guard-destructive.sh"
RAW="https://raw.githubusercontent.com/mvdatacenter/claude-instructions/main/hooks/guard-destructive.sh"

if [ ! -f "$SCRIPT" ]; then
    mkdir -p .claude-shared
    TOKEN=$(gh auth token 2>/dev/null)
    curl -sf -H "Authorization: token $TOKEN" "$RAW" -o "$SCRIPT"
fi

[ -f "$SCRIPT" ] && bash "$SCRIPT"
