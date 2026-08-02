#!/usr/bin/env python3
"""Tests for verify_citations.py."""

import pytest

import verify_citations
from verify_citations import find_source_files, normalize_ref, search_passage_in_text


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
def test_bacchae_registry_hints_find_unnumbered_passages(passage, text, expected):
    snippet = search_passage_in_text(text, passage, "euripides:bacchae")

    assert expected in snippet


def test_registered_hint_falls_back_to_generic_section_search():
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


def epiphanius_sources_dir(tmp_path):
    source_dir = tmp_path / "patristic" / "epiphanius_panarion"
    source_dir.mkdir(parents=True)
    for name in ("book51.txt", "full.txt"):
        (source_dir / name).write_text("placeholder", encoding="utf-8")
    return tmp_path


def selected_file_names(tmp_path, passage, monkeypatch):
    monkeypatch.setattr(verify_citations, "SOURCES_DIR", epiphanius_sources_dir(tmp_path))
    ref = normalize_ref(passage) if passage is not None else None
    return [f.name for f in find_source_files("epiphanius:panarion", ref=ref)]


def test_reference_without_a_book_number_searches_general_files_first(tmp_path, monkeypatch):
    assert selected_file_names(tmp_path, "42", monkeypatch) == ["full.txt", "book51.txt"]


def test_reference_with_a_book_number_searches_that_book_first(tmp_path, monkeypatch):
    assert selected_file_names(tmp_path, "51.22", monkeypatch) == ["book51.txt", "full.txt"]


def test_citation_without_a_passage_keeps_alphabetical_order(tmp_path, monkeypatch):
    assert selected_file_names(tmp_path, None, monkeypatch) == ["book51.txt", "full.txt"]


def test_hints_only_search_suppresses_the_section_number_fallback():
    text = "7. A same-numbered section in the wrong file.\n"

    snippet = search_passage_in_text(text, "16.2.7", "example:source", hints_only=True)

    assert snippet == ""


def test_registered_hint_in_a_later_file_beats_an_earlier_section_match(tmp_path, monkeypatch):
    """The hinted passage sits in book16ch2.txt, but book16ch1.txt sorts first
    and contains a bare section-number match. The hint must win."""
    source_dir = tmp_path / "ancient" / "example_source"
    source_dir.mkdir(parents=True)
    (source_dir / "book16ch1.txt").write_text(
        "7. A same-numbered section in the wrong chapter file.\n",
        encoding="utf-8",
    )
    (source_dir / "book16ch2.txt").write_text(
        "The hinted passage about the dragon begins here.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(verify_citations, "SOURCES_DIR", tmp_path)
    monkeypatch.setitem(
        verify_citations.SOURCES,
        "example:source",
        {
            "category": "ancient",
            "urls": {},
            "passage_hints": {7: [r"hinted passage about the dragon"]},
        },
    )
    citation = verify_citations.Citation(
        file="chapter5.tex",
        line_num=1,
        key="example:source",
        passage="16.2.7",
        context="",
    )

    verify_citations.verify_citation(citation)

    assert citation.status == "LOCATED"
    assert citation.snippet.startswith("[book16ch2.txt]")
