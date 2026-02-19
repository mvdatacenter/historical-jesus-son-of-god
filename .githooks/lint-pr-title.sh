#!/bin/bash
# PreToolUse hook: validates PR titles follow conventional commit format.
#
# Intercepts `gh pr create` commands and checks the --title argument.
# Exit 0 = allow, exit 2 = block.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only check gh pr create commands
if ! echo "$COMMAND" | grep -qE '^\s*gh\s+pr\s+create\b'; then
    exit 0
fi

# Extract title from --title "..." or --title="..." or -t "..."
TITLE=""
if echo "$COMMAND" | grep -qE -- '--title[= ]'; then
    TITLE=$(echo "$COMMAND" | sed -nE 's/.*--title[= ]["'"'"']([^"'"'"']+)["'"'"'].*/\1/p')
fi
if [ -z "$TITLE" ] && echo "$COMMAND" | grep -qE -- '-t '; then
    TITLE=$(echo "$COMMAND" | sed -nE 's/.*-t ["'"'"']([^"'"'"']+)["'"'"'].*/\1/p')
fi

# If we couldn't extract a title, allow (may be interactive or using a different format)
if [ -z "$TITLE" ]; then
    exit 0
fi

# Validate conventional commit format
if ! echo "$TITLE" | grep -qE '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?!?: .+'; then
    echo "BLOCKED: PR title does not follow conventional commit format." >&2
    echo "" >&2
    echo "Expected: <type>: <description>" >&2
    echo "Got: $TITLE" >&2
    echo "" >&2
    echo "Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  feat: add user authentication" >&2
    echo "  fix: resolve null pointer in parser" >&2
    exit 2
fi

exit 0
