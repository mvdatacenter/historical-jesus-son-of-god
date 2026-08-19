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

    assert perseus_section_links(html, doc) == [1, 117]


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

    assert fetched_urls == [
        "https://www.perseus.tufts.edu/hopper/text?"
        "doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D2%3Asection%3D1",
        "https://www.perseus.tufts.edu/hopper/text?"
        "doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D2%3Asection%3D117",
    ]
    assert "Full page text without section markers." not in text
    assert "Archelaus chunk." in text
    assert "Judas the Galilean chunk." in text
