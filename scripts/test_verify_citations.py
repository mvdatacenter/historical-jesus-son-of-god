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


def test_book_heading_alone_does_not_locate_a_missing_section():
    """A truncated book2.txt reported josephus:war 2.497--507 as LOCATED on
    nothing but its "Book II" heading; the heading says nothing about the
    cited section."""
    text = """Book II
1
NOW the necessity which Archelaus was under of taking a journey to
Rome was the occasion of new disturbances.
"""

    snippet = search_passage_in_text(text, "2.497--507", "josephus:war")

    assert snippet == ""


def test_bracketed_section_marker_locates_a_book_section_reference():
    text = """Book II
[
497
]
Now the people of Cesarea had slain the Jews that were among them.
"""

    snippet = search_passage_in_text(text, "2.497--507", "josephus:war")

    assert "Cesarea" in snippet


def test_a_marker_later_in_the_cited_range_locates_the_passage():
    """Chunked texts may only mark a later section of the range: book2.txt
    carries a [507] marker but no [497]."""
    text = """Book II
[
507
]
And thus were the Jews of Cesarea destroyed in one hour.
"""

    snippet = search_passage_in_text(text, "2.497--507", "josephus:war")

    assert "destroyed in one hour" in snippet


def test_a_nearby_preceding_chunk_marker_anchors_the_passage():
    """Perseus renders one marker per chunk, so War 4.317 sits inside the
    chunk marked [314]; the snippet names the anchor it reads from."""
    text = """[
310
]
Text of an earlier chunk.
[
314
]
The chunk containing the cited section. Ananus was slain here.
[
326
]
A later chunk.
"""

    snippet = search_passage_in_text(text, "4.317", "josephus:war")

    assert snippet.startswith("(from the chunk marked [314])")
    assert "Ananus" in snippet


def test_a_far_away_marker_does_not_anchor_the_passage():
    """A marker more than 40 sections before the citation is unrelated
    numbering, not the containing chunk."""
    text = """[
100
]
First chunk.
[
150
]
Second chunk.
[
200
]
Third chunk.
"""

    snippet = search_passage_in_text(text, "4.317", "josephus:war")

    assert snippet == ""


def test_sparse_numbers_do_not_anchor_as_chunk_markers():
    """A stray number (page numbering, a date) is not chunk structure, so
    it does not anchor a nearby citation."""
    text = """Some narrative text.
312
More narrative text without any chunk markers.
"""

    snippet = search_passage_in_text(text, "6.315", "example:source")

    assert snippet == ""


def test_resetting_subsection_numbers_do_not_anchor_as_chunk_markers():
    """LacusCurtius interleaves chapter markers with per-chapter subsection
    numbers (17, then 1-5, then 18, ...). A citation of chapter 15 must not
    anchor on a subsection "9" line: only numbers larger than every earlier
    number in the file read as chunk structure."""
    text = """Epitome of Book LXVI
17
1
Vespasian fell sick.
2
Portents had occurred.
9
A subsection of a much later chapter.
18
At his death Titus succeeded to the rule.
"""

    snippet = search_passage_in_text(text, "66.15", "example:source")

    assert snippet == ""


def test_a_book_reference_never_searches_a_different_book_file(tmp_path, monkeypatch):
    """A [497] marker in book3.txt located a josephus:war 2.497--507
    citation; the file for another book can only present the wrong passage."""
    source_dir = tmp_path / "patristic" / "epiphanius_panarion"
    source_dir.mkdir(parents=True)
    for name in ("book3.txt", "book51.txt", "full.txt"):
        (source_dir / name).write_text("placeholder", encoding="utf-8")
    monkeypatch.setattr(verify_citations, "SOURCES_DIR", tmp_path)

    ref = normalize_ref("51.22")
    names = [f.name for f in find_source_files("epiphanius:panarion", ref=ref)]

    assert names == ["book51.txt", "full.txt"]


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


def test_registered_hint_reaches_a_file_outside_the_cited_book(tmp_path, monkeypatch):
    """Thayer's Cassius Dio page split does not follow the citation's
    edition numbering: the passage cited as 66.15 sits on the "65" page.
    The hint pass searches every file of the source, not only the files
    the cited book number selects."""
    source_dir = tmp_path / "ancient" / "example_source"
    source_dir.mkdir(parents=True)
    (source_dir / "book65.txt").write_text(
        "Berenice was at the very height of her power.\n",
        encoding="utf-8",
    )
    (source_dir / "book66.txt").write_text(
        "Text of the next book, without the passage.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(verify_citations, "SOURCES_DIR", tmp_path)
    monkeypatch.setitem(
        verify_citations.SOURCES,
        "example:source",
        {
            "category": "ancient",
            "urls": {},
            "passage_hints": {15: [r"height of her power"]},
        },
    )
    citation = verify_citations.Citation(
        file="chapter2.tex",
        line_num=1,
        key="example:source",
        passage="66.15",
        context="",
    )

    verify_citations.verify_citation(citation)

    assert citation.status == "LOCATED"
    assert citation.snippet.startswith("[book65.txt]")


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
