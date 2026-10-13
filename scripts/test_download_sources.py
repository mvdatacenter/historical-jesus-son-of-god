#!/usr/bin/env python3
"""Tests for download_sources.py."""

import download_sources
from download_sources import (
    _present_sections,
    complete_perseus_book,
    download_url,
    perseus_section_links,
)


def test_present_sections_reads_bracket_and_bare_line_markers():
    text = """Book II
1
2
Some narrative text follows the bare markers.
[250]
More text after a bracketed marker, and an inline [261] marker too.
In the year 4004 nothing is marked.
"""

    sections = _present_sections(text)

    assert {1, 2, 250, 261} <= sections
    assert 4004 not in sections


def test_redirect_to_site_root_is_a_failed_download(tmp_path, monkeypatch):
    """classics.mit.edu redirected every http:// page URL to its homepage,
    which cached the homepage as source text for 17 files. A response whose
    final URL dropped the requested path is a dead page, not a download."""

    class FakeResponse:
        url = "https://classics.mit.edu/"
        text = "<html>homepage</html>"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        download_sources.requests, "get", lambda *a, **k: FakeResponse()
    )
    monkeypatch.setattr(download_sources.time, "sleep", lambda seconds: None)
    dest = tmp_path / "full.txt"

    ok = download_url("http://classics.mit.edu/Plato/stateman.html", dest)

    assert ok is False
    assert not dest.exists()


def test_perseus_section_links_reads_only_the_requested_doc():
    doc = "Perseus%3Atext%3A1999.01.0148%3Abook%3D2"
    html = (
        '<a href="?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D2%3Asection%3D1">1</a>'
        '<a href="?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D2%3Asection%3D117">117</a>'
        '<a href="?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D1%3Asection%3D99">99</a>'
    )

    assert perseus_section_links(html, doc) == ("section", [1, 117])


def test_perseus_section_links_reads_chapter_links():
    """Perseus splits Bostock and Riley's Pliny by chapter: the book 16 page
    carries only ...book%3D16%3Achapter%3D<n> links, which the section-only
    pattern missed, saving chapters 1-10 of 95 as the whole book (#187)."""
    doc = "Perseus%3Atext%3A1999.02.0137%3Abook%3D16"
    html = (
        '<a href="?doc=Perseus%3Atext%3A1999.02.0137%3Abook%3D16%3Achapter%3D1">1</a>'
        '<a href="?doc=Perseus%3Atext%3A1999.02.0137%3Abook%3D16%3Achapter%3D76">76</a>'
        '<a href="?doc=Perseus%3Atext%3A1999.02.0137%3Abook%3D17%3Achapter%3D3">3</a>'
    )

    assert perseus_section_links(html, doc) == ("chapter", [1, 76])


def test_present_sections_reads_chapter_headings_not_footnote_numbers():
    """Bostock heads chapters "CHAP. I.—" or "CHAP. 3. (4.)—" and prints
    footnote numbers as bare lines; for chapters only the heading counts."""
    text = """BOOK XVI. THE NATURAL HISTORY OF THE FOREST TREES.
CHAP. I.—COUNTRIES THAT HAVE NO TREES.
food and the various aliments
8
CHAP. 3. (4.)—THE ACORN OAK. THE CIVIC CROWN.
It is with the leaves of this class of trees
CHAP. XIV.—A ROMAN NUMERAL HEADING.
"""

    assert _present_sections(text, "chapter") == {1, 3, 14}


def _complete_with_fake_chunks(monkeypatch, url, html, page_text, chunks):
    """Run complete_perseus_book with each chunk URL answered by the text in
    chunks whose key ends that URL; return the book and the URLs fetched."""
    fetched_urls = []

    class FakeResponse:
        def __init__(self, chunk_url):
            self.text = chunk_url

        def raise_for_status(self):
            pass

    def fake_get(chunk_url, headers=None, timeout=None):
        fetched_urls.append(chunk_url)
        return FakeResponse(chunk_url)

    def fake_clean(html_content, url=""):
        for suffix, chunk_text in chunks.items():
            if html_content.endswith(suffix):
                return chunk_text
        raise AssertionError(f"unexpected chunk fetch: {html_content}")

    monkeypatch.setattr(download_sources.requests, "get", fake_get)
    monkeypatch.setattr(download_sources.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(download_sources, "clean_html_to_text", fake_clean)

    text = complete_perseus_book(url, html, page_text)
    return text, fetched_urls


def test_complete_perseus_book_builds_the_book_from_its_chunks(monkeypatch):
    """The nav offers sections 1, 2 and 117; sections 1 and 2 share a chunk.
    The book is built from chunk fetches alone — the book page's own
    rendering (first chunk or full text, either way sparsely marked) is
    discarded, and a chunk is fetched only for sections no fetched chunk
    already marked."""
    url = "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D2"
    html = (
        '<a href="?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D2%3Asection%3D1">1</a>'
        '<a href="?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D2%3Asection%3D2">2</a>'
        '<a href="?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D2%3Asection%3D117">117</a>'
    )
    page_text = "Book II\nFull page text without section markers.\n"

    chunks = {
        "%3Asection%3D1": "[1]\nArchelaus chunk.\n[2]\nStill the Archelaus chunk.\n",
        "%3Asection%3D117": "[117]\nJudas the Galilean chunk.\n",
    }

    text, fetched_urls = _complete_with_fake_chunks(
        monkeypatch, url, html, page_text, chunks
    )

    assert fetched_urls == [
        "https://www.perseus.tufts.edu/hopper/text?"
        "doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D2%3Asection%3D1",
        "https://www.perseus.tufts.edu/hopper/text?"
        "doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D2%3Asection%3D117",
    ]
    assert "Full page text without section markers." not in text
    assert "Archelaus chunk." in text
    assert "Judas the Galilean chunk." in text


def test_complete_perseus_book_follows_chapter_links(monkeypatch):
    """A chapter-split book is built from its chapter chunks, fetched by
    chapter URL; footnote numbers in one chunk do not mark later chapters
    as covered, so chapter 76 is still fetched (#187)."""
    doc = "Perseus%3Atext%3A1999.02.0137%3Abook%3D16"
    url = f"https://www.perseus.tufts.edu/hopper/text?doc={doc}"
    html = "".join(
        f'<a href="?doc={doc}%3Achapter%3D{n}">{n}</a>' for n in (1, 2, 76)
    )
    page_text = "BOOK XVI.\nCHAP. I.—COUNTRIES THAT HAVE NO TREES.\n"

    chunks = {
        "%3Achapter%3D1": "CHAP. I.—COUNTRIES THAT HAVE NO TREES.\nfood\n2\n76\n",
        "%3Achapter%3D2": "CHAP. 2.—WONDERS CONNECTED WITH TREES.\nforests\n",
        "%3Achapter%3D76": "CHAP. 76.—THE SIZE OF TREES.\nthe fir\n",
    }

    text, fetched_urls = _complete_with_fake_chunks(
        monkeypatch, url, html, page_text, chunks
    )

    assert fetched_urls == [f"{url}%3Achapter%3D{n}" for n in (1, 2, 76)]
    assert "the fir" in text
