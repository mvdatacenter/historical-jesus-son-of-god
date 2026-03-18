#!/usr/bin/env python3
"""
chatgpt_cli.py — CLI for ChatGPT Desktop App operations.

Entry point installed via pyproject.toml:
    poetry run chatgpt read              — read latest response (passive)
    poetry run chatgpt send "query"      — send a query
    poetry run chatgpt scrape --limit N  — scrape conversation history
"""

import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def main():
    if len(sys.argv) < 2:
        print("Usage: chatgpt <read|send|scrape> [args...]", file=sys.stderr)
        print("", file=sys.stderr)
        print("  chatgpt read              Read latest ChatGPT response", file=sys.stderr)
        print('  chatgpt send "query"      Send query to ChatGPT', file=sys.stderr)
        print("  chatgpt scrape --limit N  Scrape conversation history", file=sys.stderr)
        sys.exit(1)

    subcmd = sys.argv[1]
    rest = sys.argv[2:]

    if subcmd == "read":
        _run(["python", str(SCRIPT_DIR / "chatgpt_desktop.py"), "read_latest"] + rest)

    elif subcmd == "send":
        _run(["python", str(SCRIPT_DIR / "ask_chatgpt.py")] + rest)

    elif subcmd == "scrape":
        _run([
            "python", str(SCRIPT_DIR / "chatgpt_desktop.py"),
            "extensive_scrape_history",
            "--user-gave-me-very-explicit-instruction-to-scrape",
        ] + rest)

    else:
        print(f"Unknown subcommand: {subcmd}", file=sys.stderr)
        sys.exit(1)


def _run(cmd):
    result = subprocess.run(cmd, cwd=SCRIPT_DIR.parent)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
