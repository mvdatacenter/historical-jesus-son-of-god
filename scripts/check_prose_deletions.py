#!/usr/bin/env python3
"""Report prose removed from manuscript files so deletions cannot pass unnoticed.

A manuscript claim the author cannot confirm stays in the book and becomes a
research question (see docs/PM_0007). The failure that motivated this check was
not a deliberate removal but a concealed one: deletions interleaved with
insertions inside a large rework left the diffstat reading as growth while a
section's thesis paragraph was gone. This prints every removed prose line so the
author must account for each one in the PR body.

Usage:
    python3 scripts/check_prose_deletions.py [base]

Exits 1 when prose was removed, 0 otherwise. `base` defaults to origin/main.
"""

from __future__ import annotations

import subprocess
import sys

MANUSCRIPT_GLOBS = ["chapter*.tex", "preface.tex", "epilogue.tex"]


def parse_removals(diff: str) -> list[tuple[str, str]]:
    """Return (file, text) for each removed line in `diff` that carries prose."""
    removals: list[tuple[str, str]] = []
    current = ""
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
        elif line.startswith("-") and not line.startswith("---"):
            text = line[1:].strip()
            if text:
                removals.append((current, text))
    return removals


def removed_prose_lines(base: str) -> list[tuple[str, str]]:
    """Return (file, text) for each prose line removed against `base`."""
    diff = subprocess.run(
        ["git", "diff", "--unified=0", f"{base}...HEAD", "--", *MANUSCRIPT_GLOBS],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return parse_removals(diff)


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    removals = removed_prose_lines(base)
    if not removals:
        print(f"No manuscript prose removed against {base}.")
        return 0

    print(f"{len(removals)} prose line(s) removed against {base}.")
    print("Enumerate each in the PR body with the reason it was removed, and")
    print("confirm the user agreed to the removal of that specific passage.")
    print()
    for path, text in removals:
        print(f"  {path}: {text}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
