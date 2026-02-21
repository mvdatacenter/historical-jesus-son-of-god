#!/usr/bin/env python3
"""
verify_citations.py — Parse \\cite commands from chapters and verify against downloaded texts.

Extracts all \\cite[passage]{key} commands from chapter*.tex files,
checks whether the referenced source text has been downloaded,
and attempts to locate the cited passage within the downloaded text.

Usage:
    poetry run python scripts/verify_citations.py                    # All chapters
    poetry run python scripts/verify_citations.py --chapter 4        # Chapter 4 only
    poetry run python scripts/verify_citations.py --key josephus:war # Single source
    poetry run python scripts/verify_citations.py --summary          # Summary only
    poetry run python scripts/verify_citations.py --review           # Human review report
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_registry import SOURCES, MODERN

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = PROJECT_ROOT / "sources"
REPORT_PATH = SOURCES_DIR / "verification_report.md"

SNIPPET_LENGTH = 300
DEEP_SNIPPET_LENGTH = 2000

# Regex to match \cite[optional]{key} and \cite{key1,key2}
CITE_PATTERN = re.compile(
    r"\\cite"
    r"(?:\[([^\]]*)\])?"  # optional passage in brackets
    r"\{([^}]+)\}"        # one or more keys in braces
)


@dataclass
class Citation:
    """A single citation found in a .tex file."""
    file: str
    line_num: int
    key: str
    passage: str  # "" if no passage specified
    context: str  # surrounding text from the .tex file
    status: str = "PENDING"  # LOCATED / NOT_FOUND / NO_SOURCE / MODERN / NO_PASSAGE
    snippet: str = ""  # extracted text snippet if found
    claim_text: str = ""  # cleaned claim from .tex


def extract_citations(tex_path):
    """Extract all citations from a single .tex file."""
    citations = []
    text = tex_path.read_text(encoding="utf-8")

    for line_num, line in enumerate(text.split("\n"), 1):
        # Skip comments
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue

        for match in CITE_PATTERN.finditer(line):
            passage = match.group(1) or ""
            keys_str = match.group(2)

            # Handle multiple keys: \cite{key1,key2,key3}
            keys = [k.strip() for k in keys_str.split(",")]

            # Get context: the line of text this citation appears in
            context_line = line.strip()
            # Trim to reasonable length
            if len(context_line) > 200:
                # Find the cite command position and extract around it
                start = max(0, match.start() - 80)
                end = min(len(line), match.end() + 80)
                context_line = "..." + line[start:end].strip() + "..."

            for key in keys:
                citations.append(Citation(
                    file=tex_path.name,
                    line_num=line_num,
                    key=key,
                    passage=passage,
                    context=context_line,
                ))

    return citations


def extract_claim(tex_path, line_num):
    """Extract the manuscript's claim around a citation line.

    Reads 5 lines before and 10 lines after the citation to capture
    the full claim context including any quote blocks. Then strips
    LaTeX commands.
    """
    text = tex_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    # line_num is 1-indexed
    idx = line_num - 1
    start = max(0, idx - 5)
    end = min(len(lines), idx + 11)

    # If there's a \begin{quote} after the cite, extend to \end{quote}
    for i in range(idx, min(len(lines), idx + 15)):
        if "\\begin{quote}" in lines[i]:
            # Find the matching \end{quote}
            for j in range(i + 1, min(len(lines), i + 20)):
                if "\\end{quote}" in lines[j]:
                    end = max(end, j + 2)
                    break
            break

    claim_lines = lines[start:end]
    claim_text = "\n".join(claim_lines)
    # Strip LaTeX commands but preserve text content
    claim_text = re.sub(r"\\begin\{quote\}", "", claim_text)
    claim_text = re.sub(r"\\end\{quote\}", "", claim_text)
    claim_text = re.sub(r"\\(?:emph|textit|textbf|textsc)\{([^}]*)\}", r"\1", claim_text)
    claim_text = re.sub(r"\\cite\[[^\]]*\]\{[^}]*\}", "", claim_text)
    claim_text = re.sub(r"\\cite\{[^}]*\}", "", claim_text)
    claim_text = re.sub(r"\\footnote\{[^}]*\}", "", claim_text)
    claim_text = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", claim_text)
    claim_text = re.sub(r"\\[a-zA-Z]+\*?", "", claim_text)
    claim_text = re.sub(r"[{}]", "", claim_text)
    # Collapse whitespace but preserve paragraph breaks
    claim_text = re.sub(r"[ \t]+", " ", claim_text)
    claim_text = re.sub(r"\n\s*\n", "\n", claim_text)
    return claim_text.strip()


def find_source_files(key, ref=None):
    """Find all downloaded text files for a given bib key.

    When ref includes a book number, prioritize the matching book file
    (e.g., book5.txt first when ref has book=5) to avoid wrong-file matches.
    """
    source_info = SOURCES.get(key)
    if not source_info:
        return []

    category = source_info["category"]
    safe_key = key.replace(":", "_")
    source_dir = SOURCES_DIR / category / safe_key

    if not source_dir.exists():
        return []

    files = sorted(source_dir.glob("*.txt"))

    # Prioritize book file matching the reference
    if ref and ref.get("book"):
        book_num = ref["book"]
        priority = [f for f in files if f"book{book_num}" in f.name]
        rest = [f for f in files if f not in priority]
        return priority + rest

    return files


def normalize_ref(passage):
    """Parse a passage reference into searchable components.

    Examples:
        "4.618"       -> book=4, section=618
        "18.1--10"    -> book=18, section=1
        "2.117--118"  -> book=2, section=117
        "5.19.4"      -> book=5, chapter=19, section=4
        "3.39"        -> book=3, section=39
        "§14"         -> section=14
        "83--84"      -> section=83
        "Vision 1--4" -> keyword="Vision", number=1
        "Book 1"      -> keyword="Book", number=1
        "Life of Sertorius 26" -> keyword="Sertorius", number=26
        "13.27"       -> book=13, section=27
    """
    passage = passage.strip()
    if not passage:
        return {}

    result = {}

    # Handle "Life of Sertorius 26" style
    life_match = re.match(r"Life\s+of\s+(\w+)\s+(\d+)", passage)
    if life_match:
        result["keyword"] = life_match.group(1)
        result["number"] = int(life_match.group(2))
        return result

    # Handle comma-separated refs: "Vision 3, Similitude 9"
    if "," in passage:
        parts = [p.strip() for p in passage.split(",")]
        # Parse first part as primary, store all parts for search
        result = normalize_ref(parts[0])
        result["extra_keywords"] = []
        for part in parts[1:]:
            sub = normalize_ref(part)
            if sub.get("keyword") and sub.get("number"):
                result["extra_keywords"].append(sub)
        return result

    # Handle "Vision 1--4", "Book 1", "Similitude 9" style
    keyword_match = re.match(r"([A-Za-z]+)\s+(\d+)", passage)
    if keyword_match and not re.match(r"\d", passage):
        result["keyword"] = keyword_match.group(1)
        result["number"] = int(keyword_match.group(2))
        return result

    # Handle §14 style
    section_match = re.match(r"§\s*(\d+)", passage)
    if section_match:
        result["section"] = int(section_match.group(1))
        return result

    # Handle numeric references: "5.19.4", "18.1--10", "4.618", "83--84"
    # Remove range suffixes: "1--10" -> "1"
    clean = re.sub(r"--?\d+", "", passage)
    # Remove semicolons (multiple refs): "1.81; 4.123--125" -> take first
    if ";" in clean:
        clean = clean.split(";")[0].strip()

    parts = re.findall(r"\d+", clean)
    if len(parts) >= 3:
        result["book"] = int(parts[0])
        result["chapter"] = int(parts[1])
        result["section"] = int(parts[2])
    elif len(parts) == 2:
        result["book"] = int(parts[0])
        result["section"] = int(parts[1])
    elif len(parts) == 1:
        result["section"] = int(parts[0])

    return result


def search_passage_in_text(text, passage, key, deep=False):
    """Search for a passage reference within downloaded text. Returns snippet or empty string."""
    ref = normalize_ref(passage)
    if not ref:
        return ""

    max_snippet = DEEP_SNIPPET_LENGTH if deep else SNIPPET_LENGTH
    lines = text.split("\n")
    total_text = text

    # Strategy 1: Search for section numbers in common patterns
    section = ref.get("section")
    chapter = ref.get("chapter")
    book = ref.get("book")
    keyword = ref.get("keyword")
    number = ref.get("number")

    search_patterns = []

    if keyword and number:
        # "Vision 1", "Similitude 9", "Chapter 14"
        search_patterns.append(rf"{keyword}\s+{number}\b")
        search_patterns.append(rf"{keyword}\s+{_roman(number)}\b")
        # Ordinal words: "Third Vision", "Ninth Similitude"
        ord_word = _ordinal(number)
        if ord_word:
            search_patterns.append(rf"{ord_word}\s+{keyword}")
            # Also try "Fourth Chapter" (ordinal before Chapter, common in older translations)
            search_patterns.append(rf"{ord_word}\s+Chapter")
        # Standalone number on its own line (e.g., Plutarch chapter "26")
        search_patterns.append(rf"^\s*{number}\s*$")
        search_patterns.append(rf"Chapter\s+{number}\b")

    # Also search for extra_keywords from comma-separated refs
    for extra in ref.get("extra_keywords", []):
        ek, en = extra.get("keyword"), extra.get("number")
        if ek and en:
            search_patterns.append(rf"{ek}\s+{en}\b")
            search_patterns.append(rf"{ek}\s+{_roman(en)}\b")
            ord_word = _ordinal(en)
            if ord_word:
                search_patterns.append(rf"{ord_word}\s+{ek}")

    if section:
        # Common section numbering patterns
        search_patterns.extend([
            rf"\b{section}\.\s",           # "618. " (Whiston-style numbering)
            rf"\b{section}\.$",            # "14." at end of line
            rf"^\s*{section}\s*$",         # "14" on its own line
            rf"\b{section}\)",             # "618)" numbered paragraphs
            rf"\[{section}\]",             # "[27]" bracket style
            rf"§\s*{section}\b",           # "§14"
            rf"Chapter\s+{section}\b",     # "Chapter 39"
            rf"Section\s+{section}\b",     # "Section 14"
        ])

    if book and section:
        # Try "Book X ... Chapter/Section Y" proximity
        search_patterns.append(rf"(?:Book|BOOK)\s+(?:{book}|{_roman(book)})")

    if chapter and section:
        search_patterns.append(rf"Chapter\s+{chapter}")

    # Try each pattern
    for pattern in search_patterns:
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                # Found! Extract context around match
                if deep:
                    # In deep mode, extract more lines for analysis
                    start = max(0, i - 5)
                    end = min(len(lines), i + 40)
                else:
                    start = max(0, i - 2)
                    end = min(len(lines), i + 5)
                snippet = "\n".join(lines[start:end])
                if len(snippet) > max_snippet:
                    snippet = snippet[:max_snippet] + "..."
                return snippet

    # Strategy 2: Source-specific fingerprints for known difficult passages
    # Used when standard section-number search fails (e.g., Stephanus/Bekker
    # pagination not embedded in plain-text downloads, or unusual numbering).
    fingerprints = {
        ("pliny:letters", 96): [r"Cognitionibus", r"Christianis\s+interfui"],
        # Gospel of Peter — verse numbers are inline, "24 he did" near "Garden of Joseph"
        ("gospelpeter", 24): [r"Garden of Joseph"],
        # Plato Statesman 275b-c — Stephanus pagination absent; shepherd passage
        ("plato:statesman", 275): [r"God himself was their shepherd"],
        # Plato Republic 514a-520a — Stephanus pagination absent; Cave allegory (Book VII)
        ("plato:republic", 514): [r"underground den.*open towards the light",
                                   r"BOOK VII.*enlightenment"],
        # Aristotle Poetics 1453a — Bekker pagination absent; hamartia passage
        ("aristotle:poetics", 1453): [r"error or frailty"],
        # Euripides Bacchae 434-518 — line numbers not embedded; arrest scene
        ("euripides:bacchae", 434): [r"bind me not.*reason addressing madness"],
    }
    fp_key = (key, section) if section else None
    if fp_key and fp_key in fingerprints:
        for fp_pattern in fingerprints[fp_key]:
            for i, line in enumerate(lines):
                if re.search(fp_pattern, line, re.IGNORECASE):
                    if deep:
                        start = max(0, i - 5)
                        end = min(len(lines), i + 40)
                    else:
                        start = max(0, i - 2)
                        end = min(len(lines), i + 5)
                    snippet = "\n".join(lines[start:end])
                    if len(snippet) > max_snippet:
                        snippet = snippet[:max_snippet] + "..."
                    return snippet

    # Strategy 3: Broad keyword search for distinctive terms
    # e.g., for Josephus war 4.618, search for "Vespasian" near "618"
    if section and section > 100:
        # For large section numbers, just search for the number
        pattern = rf"\b{section}\b"
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                if deep:
                    start = max(0, i - 3)
                    end = min(len(lines), i + 20)
                else:
                    start = max(0, i - 1)
                    end = min(len(lines), i + 3)
                snippet = "\n".join(lines[start:end])
                if len(snippet) > max_snippet:
                    snippet = snippet[:max_snippet] + "..."
                return snippet

    return ""


def _roman(n):
    """Convert integer to Roman numeral string."""
    vals = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    result = ""
    for value, numeral in vals:
        while n >= value:
            result += numeral
            n -= value
    return result


_ORDINALS = {
    1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth",
    6: "Sixth", 7: "Seventh", 8: "Eighth", 9: "Ninth", 10: "Tenth",
    11: "Eleventh", 12: "Twelfth",
}


def _ordinal(n):
    """Convert integer to ordinal word (e.g., 3 -> 'Third')."""
    return _ORDINALS.get(n, "")


def verify_citation(citation, deep=False):
    """Verify a single citation against downloaded sources."""
    key = citation.key

    # Check if source exists in registry
    if key not in SOURCES:
        citation.status = "UNKNOWN_KEY"
        return

    source_info = SOURCES[key]

    # Modern works: check if downloaded text exists, otherwise mark as MODERN
    if source_info["category"] == MODERN:
        ref = normalize_ref(citation.passage) if citation.passage else None
        source_files = find_source_files(key, ref=ref)
        if not source_files:
            citation.status = "MODERN"
            citation.snippet = f"See sources/modern/README.md — {source_info.get('obtain', '')}"
            return
        # Has downloaded text — fall through to normal verification

    # Find downloaded files (prioritize matching book file)
    ref = normalize_ref(citation.passage) if citation.passage else None
    source_files = find_source_files(key, ref=ref)
    if not source_files:
        citation.status = "NO_SOURCE"
        return

    # If no passage specified, just confirm source exists
    if not citation.passage:
        citation.status = "NO_PASSAGE"
        citation.snippet = f"Source downloaded ({len(source_files)} files). No specific passage to verify."
        return

    # Search for passage in downloaded texts
    for fpath in source_files:
        text = fpath.read_text(encoding="utf-8", errors="replace")
        snippet = search_passage_in_text(text, citation.passage, key, deep=deep)
        if snippet:
            citation.status = "LOCATED"
            citation.snippet = f"[{fpath.name}] {snippet}"
            return

    citation.status = "NOT_FOUND"
    citation.snippet = f"Searched {len(source_files)} file(s). Passage '{citation.passage}' not located."


def generate_report(citations, output_path):
    """Generate a Markdown verification report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Group by status
    by_status = {}
    for c in citations:
        by_status.setdefault(c.status, []).append(c)

    # Group by chapter
    by_chapter = {}
    for c in citations:
        by_chapter.setdefault(c.file, []).append(c)

    lines = [
        "# Citation Verification Report",
        "",
        f"Generated by `verify_citations.py`",
        "",
        "## Summary",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
    ]

    status_order = ["LOCATED", "NO_PASSAGE", "MODERN", "NOT_FOUND", "NO_SOURCE", "UNKNOWN_KEY"]
    for status in status_order:
        count = len(by_status.get(status, []))
        if count > 0:
            lines.append(f"| {status} | {count} |")

    lines.append(f"| **TOTAL** | **{len(citations)}** |")
    lines.append("")

    # Status legend
    lines.extend([
        "### Status Legend",
        "",
        "- **LOCATED**: Passage located in downloaded text (human review required)",
        "- **NO_PASSAGE**: Source downloaded but no specific passage cited (general reference)",
        "- **MODERN**: Copyrighted modern work (see sources/modern/README.md)",
        "- **NOT_FOUND**: Source downloaded but passage not located (may need manual check)",
        "- **NO_SOURCE**: Source not yet downloaded",
        "- **UNKNOWN_KEY**: Bibliography key not in source_registry.py",
        "",
    ])

    # Detailed results by chapter
    for chapter_file in sorted(by_chapter.keys()):
        chapter_cites = by_chapter[chapter_file]
        lines.append(f"## {chapter_file}")
        lines.append("")

        for c in sorted(chapter_cites, key=lambda x: x.line_num):
            status_icon = {
                "LOCATED": "OK",
                "NO_PASSAGE": "~~",
                "MODERN": "$$",
                "NOT_FOUND": "??",
                "NO_SOURCE": "!!",
                "UNKNOWN_KEY": "XX",
            }.get(c.status, "??")

            passage_str = f"[{c.passage}]" if c.passage else ""
            lines.append(f"### [{status_icon}] `\\cite{passage_str}{{{c.key}}}` (line {c.line_num})")
            lines.append("")
            lines.append(f"**Status:** {c.status}")
            lines.append("")

            if c.snippet:
                lines.append(f"**Detail:**")
                lines.append(f"```")
                lines.append(c.snippet[:500])
                lines.append(f"```")
                lines.append("")

            # Show context from the .tex file
            lines.append(f"**TeX context:** `{c.context[:150]}`")
            lines.append("")

    report = "\n".join(lines)
    output_path.write_text(report, encoding="utf-8")
    return report


REVIEW_REPORT_PATH = SOURCES_DIR / "citation_review.html"


def _html_escape(text):
    """Escape HTML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _source_description(citation):
    """Build the right-column content for a citation.

    LOCATED: show the source passage text.
    NO_PASSAGE: general reference — show source title/author.
    MODERN: copyrighted — show obtain instructions.
    NOT_FOUND: passage not located — note for reviewer.
    NO_SOURCE / UNKNOWN_KEY: source not downloaded or unknown.
    """
    source_info = SOURCES.get(citation.key, {})
    title = source_info.get("title", citation.key)
    author = source_info.get("author", "")

    if citation.status == "LOCATED":
        return _html_escape(citation.snippet)

    if citation.status == "NO_PASSAGE":
        desc = f"General reference to: {author}, {title}" if author else f"General reference to: {title}"
        if citation.snippet:
            desc += f"\n\n{citation.snippet}"
        return _html_escape(desc)

    if citation.status == "MODERN":
        obtain = source_info.get("obtain", "See sources/modern/README.md")
        return _html_escape(f"Modern copyrighted work: {author}, {title}\n\n{obtain}")

    if citation.status == "NOT_FOUND":
        return _html_escape(f"Source downloaded but passage not located.\n\n{citation.snippet}")

    if citation.status == "NO_SOURCE":
        return _html_escape(f"Source not yet downloaded.\nRun: poetry run python scripts/download_sources.py")

    return _html_escape(f"Unknown key: {citation.key}")


def generate_review_report(citations, output_path):
    """Generate an HTML side-by-side review report.

    Left column: what the manuscript claims (cleaned LaTeX context).
    Right column: what the source says (passage text, or description
    for general references / modern works).

    Semantic verification — whether the right column supports the left
    column — is NOT done by this script. That requires a skilled LLM or
    a human scholar reviewing each pair with full context.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Group by chapter file
    by_chapter = {}
    for c in citations:
        by_chapter.setdefault(c.file, []).append(c)

    # Count by status
    status_counts = {}
    for c in citations:
        status_counts[c.status] = status_counts.get(c.status, 0) + 1

    html_parts = [HTML_REPORT_HEAD]

    # Summary table
    html_parts.append('<div class="summary">')
    html_parts.append("<h2>Summary</h2>")
    html_parts.append("<table><tr><th>Status</th><th>Count</th><th>Meaning</th></tr>")
    status_meanings = {
        "LOCATED": "Passage found in downloaded text — needs semantic review",
        "NO_PASSAGE": "General reference, no specific passage cited",
        "MODERN": "Copyrighted modern work — not downloadable",
        "NOT_FOUND": "Source downloaded but passage not located",
        "NO_SOURCE": "Source not yet downloaded",
        "UNKNOWN_KEY": "Bibliography key not in source_registry.py",
    }
    for status in ["LOCATED", "NO_PASSAGE", "MODERN", "NOT_FOUND", "NO_SOURCE", "UNKNOWN_KEY"]:
        count = status_counts.get(status, 0)
        if count > 0:
            html_parts.append(
                f"<tr><td><code>{status}</code></td>"
                f"<td>{count}</td>"
                f"<td>{status_meanings.get(status, '')}</td></tr>"
            )
    html_parts.append(f"<tr><td><strong>TOTAL</strong></td><td><strong>{len(citations)}</strong></td><td></td></tr>")
    html_parts.append("</table></div>")

    # Citations by chapter
    entry_num = 0
    for chapter_file in sorted(by_chapter.keys()):
        chapter_cites = by_chapter[chapter_file]
        html_parts.append(f'<h2 class="chapter-heading">{_html_escape(chapter_file)}</h2>')

        for c in sorted(chapter_cites, key=lambda x: x.line_num):
            entry_num += 1
            passage_str = f"[{_html_escape(c.passage)}]" if c.passage else ""
            cite_cmd = f"\\cite{passage_str}{{{_html_escape(c.key)}}}"

            status_class = c.status.lower().replace("_", "-")

            # Left: manuscript claim
            claim = _html_escape(c.claim_text) if c.claim_text else _html_escape(c.context)

            # Right: source text or description
            source = _source_description(c)

            html_parts.append(f'<div class="entry {status_class}">')
            html_parts.append(
                f'<div class="entry-header">'
                f'<span class="entry-num">#{entry_num}</span> '
                f'<code>{cite_cmd}</code> '
                f'<span class="meta">line {c.line_num}</span> '
                f'<span class="status-badge {status_class}">{c.status}</span>'
                f'</div>'
            )
            html_parts.append('<div class="columns">')
            html_parts.append(f'<div class="col manuscript"><h3>Manuscript</h3><pre>{claim}</pre></div>')
            html_parts.append(f'<div class="col source"><h3>Source</h3><pre>{source}</pre></div>')
            html_parts.append('</div></div>')

    html_parts.append("</body></html>")

    report = "\n".join(html_parts)
    output_path.write_text(report, encoding="utf-8")
    print(f"\nReview report written to: {output_path}")
    print(f"  {entry_num} citations ready for review")
    return report


HTML_REPORT_HEAD = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Citation Review Report</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Georgia', serif; background: #f5f5f0; color: #222; padding: 24px; max-width: 1600px; margin: 0 auto; }
  h1 { font-size: 1.6em; margin-bottom: 8px; }
  h2 { font-size: 1.3em; margin: 32px 0 12px; border-bottom: 2px solid #333; padding-bottom: 4px; }
  .process { background: #fff; border: 1px solid #ccc; border-radius: 6px; padding: 16px 20px; margin: 16px 0 32px; line-height: 1.6; }
  .process h2 { border: none; margin: 0 0 8px; font-size: 1.1em; }
  .process ol { margin-left: 20px; }
  .process li { margin-bottom: 6px; }
  .process .note { background: #fff3cd; border-left: 4px solid #856404; padding: 8px 12px; margin-top: 12px; font-size: 0.92em; }
  .summary table { border-collapse: collapse; margin: 8px 0; }
  .summary th, .summary td { border: 1px solid #aaa; padding: 4px 12px; text-align: left; }
  .summary th { background: #e8e8e0; }
  .chapter-heading { margin-top: 40px; }
  .entry { background: #fff; border: 1px solid #ddd; border-radius: 6px; margin: 16px 0; padding: 0; overflow: hidden; }
  .entry-header { background: #e8e8e0; padding: 8px 14px; font-size: 0.95em; border-bottom: 1px solid #ddd; }
  .entry-num { font-weight: bold; }
  .meta { color: #666; font-size: 0.9em; }
  .status-badge { display: inline-block; padding: 1px 8px; border-radius: 3px; font-size: 0.85em; font-weight: bold; margin-left: 8px; }
  .status-badge.located { background: #d4edda; color: #155724; }
  .status-badge.no-passage { background: #fff3cd; color: #856404; }
  .status-badge.modern { background: #d1ecf1; color: #0c5460; }
  .status-badge.not-found { background: #f8d7da; color: #721c24; }
  .status-badge.no-source { background: #f8d7da; color: #721c24; }
  .status-badge.unknown-key { background: #e2e3e5; color: #383d41; }
  .columns { display: flex; gap: 0; min-height: 120px; }
  .col { flex: 1; padding: 12px 16px; overflow-x: auto; }
  .col.manuscript { border-right: 2px solid #ccc; background: #fafaf5; }
  .col.source { background: #f5f8fa; }
  .col h3 { font-size: 0.9em; text-transform: uppercase; color: #555; letter-spacing: 0.5px; margin-bottom: 8px; }
  .col pre { white-space: pre-wrap; word-wrap: break-word; font-family: 'Georgia', serif; font-size: 0.93em; line-height: 1.5; }
</style>
</head>
<body>
<h1>Citation Review Report</h1>

<div class="process">
<h2>Three-Step Verification Process</h2>
<ol>
<li><strong>Download</strong> (automated) &mdash; <code>poetry run python scripts/download_sources.py</code> fetches
    all public-domain source texts to <code>sources/</code>. Anyone can reproduce this step.</li>
<li><strong>Extract &amp; Present</strong> (automated) &mdash; <code>poetry run python scripts/verify_citations.py --review</code>
    extracts every <code>\\cite</code> command, locates the referenced passage in the downloaded text, and
    generates this side-by-side report. Left column = what the manuscript claims. Right column = what the
    source says (the actual passage for specific citations, or source metadata for general references).</li>
<li><strong>Semantic Verification</strong> (human or expert LLM) &mdash; A skilled reviewer reads each pair and
    judges whether the manuscript&rsquo;s claim accurately represents the source. This step is <em>never</em>
    automated by pattern matching, keyword extraction, or similarity scoring. It requires understanding
    the full context of both the argument and the source.</li>
</ol>
<div class="note">
<strong>Why not automate step 3?</strong> Keyword overlap and string similarity give false confidence.
A passage can share every keyword with a claim and still misrepresent it, or share no keywords and
accurately convey the meaning. Semantic accuracy requires judgment, not string matching.
See <code>docs/PM_0001_keyword-extraction-fake-verification.md</code>.
</div>
</div>
"""


def main():
    parser = argparse.ArgumentParser(
        description="Verify citations in chapter files against downloaded source texts."
    )
    parser.add_argument(
        "--chapter",
        type=int,
        help="Verify only a specific chapter number (e.g., 4)",
    )
    parser.add_argument(
        "--key",
        type=str,
        help="Verify only citations of a specific bib key",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary only, skip detailed report",
    )
    parser.add_argument(
        "--review",
        action="store_true",
        help="Generate side-by-side review report for human verification",
    )
    args = parser.parse_args()

    # Find chapter files
    if args.chapter:
        tex_files = list(PROJECT_ROOT.glob(f"chapter{args.chapter}.tex"))
        if not tex_files:
            print(f"ERROR: chapter{args.chapter}.tex not found")
            sys.exit(1)
    else:
        tex_files = sorted(PROJECT_ROOT.glob("chapter*.tex"))

    if not tex_files:
        print("ERROR: No chapter*.tex files found")
        sys.exit(1)

    print("=" * 70)
    print("Citation Verification")
    print("=" * 70)

    # Extract all citations
    all_citations = []
    for tex_file in tex_files:
        cites = extract_citations(tex_file)
        all_citations.extend(cites)
        print(f"  {tex_file.name}: {len(cites)} citations found")

    # Filter by key if requested
    if args.key:
        all_citations = [c for c in all_citations if c.key == args.key]
        print(f"\nFiltered to key '{args.key}': {len(all_citations)} citations")

    print(f"\nTotal citations: {len(all_citations)}")
    print(f"\nVerifying...\n")

    # Verify each citation
    for i, citation in enumerate(all_citations, 1):
        verify_citation(citation, deep=args.review)
        status_char = {
            "LOCATED": "+",
            "NO_PASSAGE": "~",
            "MODERN": "$",
            "NOT_FOUND": "?",
            "NO_SOURCE": "!",
            "UNKNOWN_KEY": "X",
        }.get(citation.status, "?")
        passage_str = f"[{citation.passage}]" if citation.passage else ""
        print(f"  [{status_char}] {citation.file}:{citation.line_num} "
              f"\\cite{passage_str}{{{citation.key}}} -> {citation.status}")

    # Print summary
    print(f"\n{'=' * 70}")
    print("Summary:")
    by_status = {}
    for c in all_citations:
        by_status.setdefault(c.status, []).append(c)

    for status in ["LOCATED", "NO_PASSAGE", "MODERN", "NOT_FOUND", "NO_SOURCE", "UNKNOWN_KEY"]:
        count = len(by_status.get(status, []))
        if count > 0:
            print(f"  {status:15s}: {count}")

    print(f"  {'TOTAL':15s}: {len(all_citations)}")

    # Generate report
    if not args.summary:
        report = generate_report(all_citations, REPORT_PATH)
        print(f"\nReport written to: {REPORT_PATH}")

    # Generate human review report (HTML, all citation types)
    if args.review:
        for citation in all_citations:
            tex_path = PROJECT_ROOT / citation.file
            citation.claim_text = extract_claim(tex_path, citation.line_num)
        generate_review_report(all_citations, REVIEW_REPORT_PATH)

    # Return exit code based on results
    not_found = len(by_status.get("NOT_FOUND", []))
    no_source = len(by_status.get("NO_SOURCE", []))
    unknown = len(by_status.get("UNKNOWN_KEY", []))
    if unknown > 0:
        print(f"\nWARNING: {unknown} citation(s) have unknown bibliography keys!")
    if no_source > 0:
        print(f"\nINFO: {no_source} source(s) not yet downloaded. "
              f"Run: poetry run python scripts/download_sources.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
