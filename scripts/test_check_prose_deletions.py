"""Tests for the manuscript prose-deletion check."""

from __future__ import annotations

import subprocess

import pytest

import check_prose_deletions
from check_prose_deletions import parse_removals, removed_prose_lines

PURE_ADDITION = """\
diff --git a/chapter2.tex b/chapter2.tex
--- a/chapter2.tex
+++ b/chapter2.tex
@@ -3,0 +4 @@ context
+Frankincense is the priestly offering.
"""

PLAIN_DELETION = """\
diff --git a/chapter2.tex b/chapter2.tex
--- a/chapter2.tex
+++ b/chapter2.tex
@@ -2 +1,0 @@ context
-The guard carried myrrh.
"""

NET_POSITIVE_REWORK = """\
diff --git a/chapter2.tex b/chapter2.tex
--- a/chapter2.tex
+++ b/chapter2.tex
@@ -2 +2,3 @@ context
-The guard carried myrrh.
+Gold belongs to the treasury.
+Incense belongs to the altar.
+Myrrh anoints the king.
"""

MULTI_FILE = """\
diff --git a/chapter2.tex b/chapter2.tex
--- a/chapter2.tex
+++ b/chapter2.tex
@@ -2 +1,0 @@ context
-The guard carried myrrh.
diff --git a/preface.tex b/preface.tex
--- a/preface.tex
+++ b/preface.tex
@@ -5 +4,0 @@ context
-This book argues for a Greco-Christian reading.
"""

WHITESPACE_ONLY = """\
diff --git a/chapter2.tex b/chapter2.tex
--- a/chapter2.tex
+++ b/chapter2.tex
@@ -2 +1,0 @@ context
-
"""


def test_pure_addition_reports_nothing() -> None:
    assert parse_removals(PURE_ADDITION) == []


def test_deletion_is_reported() -> None:
    assert parse_removals(PLAIN_DELETION) == [
        ("chapter2.tex", "The guard carried myrrh.")
    ]


def test_deletion_hidden_among_insertions_is_still_reported() -> None:
    assert parse_removals(NET_POSITIVE_REWORK) == [
        ("chapter2.tex", "The guard carried myrrh.")
    ]


def test_removals_are_attributed_to_their_own_file() -> None:
    assert parse_removals(MULTI_FILE) == [
        ("chapter2.tex", "The guard carried myrrh."),
        ("preface.tex", "This book argues for a Greco-Christian reading."),
    ]


def test_blank_line_removal_is_not_prose() -> None:
    assert parse_removals(WHITESPACE_ONLY) == []


def test_removed_prose_lines_diffs_the_manuscript_against_base(monkeypatch) -> None:
    captured: dict = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(cmd, 0, stdout=PLAIN_DELETION, stderr="")

    monkeypatch.setattr(check_prose_deletions.subprocess, "run", fake_run)

    assert removed_prose_lines("origin/main") == [
        ("chapter2.tex", "The guard carried myrrh.")
    ]
    assert captured["cmd"] == [
        "git",
        "diff",
        "--unified=0",
        "origin/main...HEAD",
        "--",
        "chapter*.tex",
        "preface.tex",
        "epilogue.tex",
    ]
    # Without check=True a failed git call yields empty stdout, which would read
    # as "no prose removed" -- the false negative this script exists to prevent.
    assert captured["kwargs"]["check"] is True


def test_removed_prose_lines_surfaces_a_git_failure(monkeypatch) -> None:
    def fake_run(cmd, **kwargs):
        raise subprocess.CalledProcessError(128, cmd, stderr="bad revision")

    monkeypatch.setattr(check_prose_deletions.subprocess, "run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        removed_prose_lines("no-such-ref")
