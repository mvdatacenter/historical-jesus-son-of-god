#!/bin/bash
# Claude Code hook - runs before any Bash command
# Creates backup branch before dangerous git operations

COMMAND="$1"
DANGEROUS_PATTERNS="git.*(reset --hard|rebase --abort|checkout.*--force|push.*--force|push.*-f)"

if echo "$COMMAND" | grep -qE "$DANGEROUS_PATTERNS"; then
    BACKUP_BRANCH="backup-$(date +%s)"
    echo "⚠️  Creating backup branch before dangerous command: $BACKUP_BRANCH"
    git branch "$BACKUP_BRANCH" 2>/dev/null
fi
