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
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_registry import SOURCES, MODERN

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = PROJECT_ROOT / "sources"
REPORT_PATH = SOURCES_DIR / "verification_report.md"

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
    status: str = "PENDING"  # FOUND / NOT_FOUND / NO_SOURCE / MODERN / NO_PASSAGE
    snippet: str = ""  # extracted text snippet if found


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


def find_source_files(key):
    """Find all downloaded text files for a given bib key."""
    source_info = SOURCES.get(key)
    if not source_info:
        return []

    category = source_info["category"]
    safe_key = key.replace(":", "_")
    source_dir = SOURCES_DIR / category / safe_key

    if not source_dir.exists():
        return []

    return sorted(source_dir.glob("*.txt"))


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


def search_passage_in_text(text, passage, key):
    """Search for a passage reference within downloaded text. Returns snippet or empty string."""
    ref = normalize_ref(passage)
    if not ref:
        return ""

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
                # Found! Extract context (5 lines around match)
                start = max(0, i - 2)
                end = min(len(lines), i + 5)
                snippet = "\n".join(lines[start:end])
                # Trim to ~300 chars
                if len(snippet) > 300:
                    snippet = snippet[:300] + "..."
                return snippet

    # Strategy 2: Broad keyword search for distinctive terms
    # e.g., for Josephus war 4.618, search for "Vespasian" near "618"
    if section and section > 100:
        # For large section numbers, just search for the number
        pattern = rf"\b{section}\b"
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                start = max(0, i - 1)
                end = min(len(lines), i + 3)
                snippet = "\n".join(lines[start:end])
                if len(snippet) > 300:
                    snippet = snippet[:300] + "..."
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


def verify_citation(citation):
    """Verify a single citation against downloaded sources."""
    key = citation.key

    # Check if source exists in registry
    if key not in SOURCES:
        citation.status = "UNKNOWN_KEY"
        return

    source_info = SOURCES[key]

    # Modern works: just note it
    if source_info["category"] == MODERN:
        citation.status = "MODERN"
        citation.snippet = f"See sources/modern/README.md — {source_info.get('obtain', '')}"
        return

    # Find downloaded files
    source_files = find_source_files(key)
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
        snippet = search_passage_in_text(text, citation.passage, key)
        if snippet:
            citation.status = "FOUND"
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

    status_order = ["FOUND", "NO_PASSAGE", "MODERN", "NOT_FOUND", "NO_SOURCE", "UNKNOWN_KEY"]
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
        "- **FOUND**: Passage located in downloaded text",
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
                "FOUND": "OK",
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
        verify_citation(citation)
        status_char = {
            "FOUND": "+",
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

    for status in ["FOUND", "NO_PASSAGE", "MODERN", "NOT_FOUND", "NO_SOURCE", "UNKNOWN_KEY"]:
        count = len(by_status.get(status, []))
        if count > 0:
            print(f"  {status:15s}: {count}")

    print(f"  {'TOTAL':15s}: {len(all_citations)}")

    # Generate report
    if not args.summary:
        report = generate_report(all_citations, REPORT_PATH)
        print(f"\nReport written to: {REPORT_PATH}")

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
