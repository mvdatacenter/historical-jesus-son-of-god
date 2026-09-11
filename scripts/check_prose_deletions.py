#!/usr/bin/env python3
"""Report prose removed from manuscript files so deletions cannot pass unnoticed.

A manuscript claim the author cannot confirm stays in the book and becomes a
research question (see docs/PM_0007). The failure that motivated this check was
not a deliberate removal but a concealed one: deletions interleaved with
insertions inside a large rework left the diffstat reading as growth while a
section's thesis paragraph was gone. This prints every removed prose line so the
author must account for each one in the PR body.

Usage:
    python3 scripts/check_prose_deletions.py [base] [--body-file PATH]

Without --body-file: exits 1 when prose was removed, 0 otherwise, so the
author sees the list before writing the body. With --body-file: exits 1 only
for a removed line the PR body does not quote, so a rework that accounts for
every removed line passes and one that drops a line silently is refused. The
tests workflow runs the second form on every pull request with the pull
request's body. `base` defaults to origin/main.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys

MANUSCRIPT_GLOBS = ["chapter*.tex", "preface.tex", "epilogue.tex"]

_CITE = re.compile(r"\\cite[a-z]*(?:\[[^\]]*\])*\{[^}]*\}")
_NON_WORD = re.compile(r"[^0-9a-z]+")


def normalize(text: str) -> str:
    """Reduce prose to lowercase words so a quotation matches its source.

    Citations, quotation marks, LaTeX escapes and punctuation differ between a
    manuscript line and the way a body quotes it; the words do not.
    """
    text = _CITE.sub(" ", text)
    return _NON_WORD.sub(" ", text.lower()).strip()


def unaccounted_lines(
    removals: list[tuple[str, str]], body: str
) -> list[tuple[str, str]]:
    """Return the removed lines whose words the body does not quote."""
    haystack = " " + normalize(body) + " "
    return [
        (path, text)
        for path, text in removals
        if " " + normalize(text) + " " not in haystack
    ]


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("base", nargs="?", default="origin/main")
    parser.add_argument(
        "--body-file",
        help="PR body to check; every removed line must be quoted in it",
    )
    args = parser.parse_args(argv)
    removals = removed_prose_lines(args.base)
    if not removals:
        print(f"No manuscript prose removed against {args.base}.")
        return 0

    if args.body_file is None:
        print(f"{len(removals)} prose line(s) removed against {args.base}.")
        print("Enumerate each in the PR body with the reason it was removed, and")
        print("confirm the user agreed to the removal of that specific passage.")
        print()
        for path, text in removals:
            print(f"  {path}: {text}")
        return 1

    with open(args.body_file, encoding="utf-8") as handle:
        body = handle.read()
    missing = unaccounted_lines(removals, body)
    if not missing:
        print(
            f"{len(removals)} prose line(s) removed against {args.base}, "
            "each quoted in the PR body."
        )
        return 0

    print(
        f"{len(missing)} of {len(removals)} prose line(s) removed against "
        f"{args.base} are not quoted in the PR body."
    )
    print("Quote each removed line in the body with the reason it was removed;")
    print("a removed claim the body does not name is a deletion nobody agreed to.")
    print()
    for path, text in missing:
        print(f"  {path}: {text}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
