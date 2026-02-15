#!/bin/bash
# Git safety hook - blocks commits/pushes to main and creates backups for dangerous commands

# Read the tool input from stdin
input=$(cat)

# Extract the command being run
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# ── BLOCK: commits and pushes on main/master ──
current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
  if echo "$command" | grep -qE "^git (commit|push)"; then
    echo "❌ BLOCKED: Cannot commit or push on '$current_branch'. Create a feature branch first." >&2
    exit 2  # exit 2 = block the command
  fi
fi

# ── BLOCK: pushing directly to main/master from any branch ──
if echo "$command" | grep -qE "git push.*(origin|upstream)\s+(main|master)"; then
  echo "❌ BLOCKED: Cannot push directly to main/master. Use a PR." >&2
  exit 2
fi

# ── WARN + BACKUP: dangerous commands ──
dangerous_patterns=(
  "git reset --hard"
  "git rebase --abort"
  "git checkout.*--force"
  "git push.*--force"
  "git push.*-f "
  "git clean -fd"
)

for pattern in "${dangerous_patterns[@]}"; do
  if echo "$command" | grep -qE "$pattern"; then
    BACKUP_BRANCH="backup-$(date +%s)"
    git branch "$BACKUP_BRANCH" 2>/dev/null
    echo "⚠️  DANGEROUS COMMAND DETECTED: $command" >&2
    echo "✓ Created backup branch: $BACKUP_BRANCH" >&2
    exit 0  # Allow but with backup
  fi
done

# Allow safe commands
exit 0
