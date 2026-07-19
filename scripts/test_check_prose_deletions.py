"""Tests for the manuscript prose-deletion check."""

from __future__ import annotations

from check_prose_deletions import parse_removals

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
