#!/bin/bash
# Git safety hook - creates backup branch before dangerous commands

# Read the tool input from stdin
input=$(cat)

# Extract the command being run
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Define dangerous patterns that need backup
dangerous_patterns=(
  "git reset --hard"
  "git rebase --abort"
  "git checkout.*--force"
  "git push.*--force"
  "git push.*-f "
  "git clean -fd"
)

# Check each pattern
for pattern in "${dangerous_patterns[@]}"; do
  if echo "$command" | grep -qE "$pattern"; then
    # Create backup branch before allowing command
    BACKUP_BRANCH="backup-$(date +%s)"
    git branch "$BACKUP_BRANCH" 2>/dev/null
    echo "⚠️  DANGEROUS COMMAND DETECTED: $command" >&2
    echo "✓ Created backup branch: $BACKUP_BRANCH" >&2
    exit 0  # Allow but with backup
  fi
done

# Allow safe commands
exit 0
