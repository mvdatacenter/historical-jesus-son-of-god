#!/usr/bin/env python3
"""Tests for verify_citations.py."""

import pytest

from verify_citations import search_passage_in_text


def test_odyssey_book_nine_ignores_gutenberg_license_number():
    text = """1.E.9. License terms
Unrelated front matter.

The Cyclops asked his name.
My name is Noman; this is what my father and mother call me.
"""

    snippet = search_passage_in_text(text, "9", "homer:odyssey")

    assert "Noman" in snippet
    assert "License terms" not in snippet


def test_odyssey_book_ten_finds_circe_passage():
    text = """BOOK X
Circe gave them drink, and when they had drunk she turned them into pigs.
They retained their human senses.
"""

    snippet = search_passage_in_text(text, "10", "homer:odyssey")

    assert "turned them into pigs" in snippet


@pytest.mark.parametrize(
    ("passage", "text", "expected"),
    [
        (
            "434",
            "The stranger never flinched, nor thought to flee when the guard arrived.",
            "never flinched",
        ),
        (
            "443",
            "The fetter and manacle fell away, and the bars slid back untouched.",
            "bars slid back untouched",
        ),
        (
            "576",
            "Spirit of the Chained Earthquake, answer the imprisoned god.",
            "Chained Earthquake",
        ),
    ],
)
def test_bacchae_fingerprints_find_unnumbered_passages(passage, text, expected):
    snippet = search_passage_in_text(text, passage, "euripides:bacchae")

    assert expected in snippet


def test_registered_fingerprint_falls_back_to_generic_section_search():
    text = """Earlier material.
443. The numbered fallback passage begins here.
Further context.
"""

    snippet = search_passage_in_text(text, "443", "euripides:bacchae")

    assert "numbered fallback passage" in snippet


def test_generic_section_search_still_handles_numbered_sources():
    text = """Earlier material.
14. The cited section begins here.
Further context.
"""

    snippet = search_passage_in_text(text, "14", "example:source")

    assert "The cited section begins here" in snippet


def test_search_returns_empty_string_when_no_passage_matches():
    snippet = search_passage_in_text(
        "This source contains no matching passage.",
        "443",
        "euripides:bacchae",
    )

    assert snippet == ""
