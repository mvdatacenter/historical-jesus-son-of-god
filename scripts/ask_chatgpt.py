#!/usr/bin/env python3
"""
ask_chatgpt.py

High-level wrapper for Claude to query ChatGPT via macOS Desktop App.

CAPABILITIES:
  1. SEND a new query and get the response:
     poetry run python scripts/ask_chatgpt.py "Your query here"

  2. READ previous turns from the ChatGPT conversation:
     poetry run python scripts/chatgpt_desktop.py read --all --limit 4
     (reads last 4 turns from the conversation)

     Options for reading:
       --all      Show all turns, not just the longest
       --latest   Show the most recent turn
       --limit N  Limit to last N turns (auto-scrolls to load them)
       --scroll   Manually scroll up to load more turns
       --debug    Show debug info about turns found

IMPORTANT FOR CLAUDE:
  - The ChatGPT Desktop App maintains a conversation history
  - You can read previous turns using the 'read' command
  - Use 'read --all --limit N' to get the last N turns from the user's conversation
  - The script will automatically scroll up to load turns when --limit is used
  - This is useful when the user says "read my last N turns from GPT"
"""

import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CHATGPT_DESKTOP_SCRIPT = SCRIPT_DIR / "chatgpt_desktop.py"


def ask_chatgpt(query: str, wait_seconds: int = 180) -> str:
    """
    Send a query to ChatGPT Desktop App and return the response.

    Args:
        query: The question/prompt to send
        wait_seconds: How long to wait for response to stabilize (default: 180s for complex queries with web search)

    Returns:
        ChatGPT's response text
    """
    full_cmd = [
        "poetry", "run", "python",
        str(CHATGPT_DESKTOP_SCRIPT),
        "send",
        "--wait-seconds", str(wait_seconds),
        query
    ]
    result = subprocess.run(
        full_cmd,
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR.parent  # Run from project root
    )

    if result.returncode != 0:
        return f"ERROR: {result.stderr}"

    return result.stdout.strip()


# Minimum query length (in sentences) to avoid lazy/brainrot queries
MIN_SENTENCES = 3


def is_wasteful_query(query: str) -> bool:
    """Block lazy queries that don't provide enough context."""
    # Count sentences (rough: split by . ! ?)
    sentences = [s.strip() for s in query.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    return len(sentences) < MIN_SENTENCES


def main():
    if len(sys.argv) < 2:
        print("Usage: ask_chatgpt.py 'Your query here'", file=sys.stderr)
        print("Or pipe query via stdin", file=sys.stderr)
        sys.exit(1)

    # Check for --i-read-the-disclaimer flag
    bypass_check = "--i-read-the-disclaimer" in sys.argv
    if bypass_check:
        sys.argv.remove("--i-read-the-disclaimer")

    # Get query from arguments or stdin
    if sys.argv[1] == "-":
        query = sys.stdin.read()
    else:
        query = " ".join(sys.argv[1:])

    # Block lazy queries unless explicitly bypassed
    if is_wasteful_query(query) and not bypass_check:
        print(f"ERROR: Query too short ({MIN_SENTENCES}+ sentences required).", file=sys.stderr)
        print("", file=sys.stderr)
        print("Short queries are evidence of brainrot. Read CLAUDE.md and provide proper context.", file=sys.stderr)
        print("", file=sys.stderr)
        print("NOTE: NEVER ask ChatGPT to repeat. Use read_latest ONLY if you lost something:", file=sys.stderr)
        print("  poetry run python scripts/chatgpt_desktop.py read_latest", file=sys.stderr)
        print("", file=sys.stderr)
        print("To bypass: add --i-read-the-disclaimer flag.", file=sys.stderr)
        sys.exit(1)

    response = ask_chatgpt(query)
    print(response)


if __name__ == "__main__":
    main()
