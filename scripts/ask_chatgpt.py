#!/usr/bin/env python3
"""
ask_chatgpt.py

High-level wrapper for Claude to query ChatGPT via macOS Desktop App.

Usage:
    poetry run python scripts/ask_chatgpt.py "Your query here"

Returns ChatGPT's response to stdout.
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


def main():
    if len(sys.argv) < 2:
        print("Usage: ask_chatgpt.py 'Your query here'", file=sys.stderr)
        print("Or pipe query via stdin", file=sys.stderr)
        sys.exit(1)

    # Get query from arguments or stdin
    if sys.argv[1] == "-":
        query = sys.stdin.read()
    else:
        query = " ".join(sys.argv[1:])

    response = ask_chatgpt(query)
    print(response)


if __name__ == "__main__":
    main()
