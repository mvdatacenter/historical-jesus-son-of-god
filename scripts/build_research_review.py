#!/usr/bin/env python3
"""Build an HTML review page for RESEARCH-verdicted findings.

Scans step2 verdict files for entries with verdict == "RESEARCH",
cross-references findings files for the finding text, resolves
YouTube source titles, and generates research_review.html.

Usage:
    python scripts/build_research_review.py
"""

import glob
import html
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COVERAGE_DIR = ROOT / "sources" / "coverage"
STEP2_DIR = COVERAGE_DIR / "step2_batches"
YOUTUBE_DIR = ROOT / "sources" / "youtube"
OUTPUT = COVERAGE_DIR / "research_review.html"


# ---------------------------------------------------------------------------
# 1. Build video_id -> title index from YouTube transcript files
# ---------------------------------------------------------------------------

def build_video_title_index() -> dict[str, str]:
    """Scan sources/youtube/*/*.txt; first line is '# Video: {title}'."""
    index: dict[str, str] = {}
    for path in glob.glob(str(YOUTUBE_DIR / "*" / "*.txt")):
        video_id = Path(path).stem
        try:
            with open(path, encoding="utf-8") as f:
                first_line = f.readline().strip()
            if first_line.startswith("# Video:"):
                title = first_line[len("# Video:"):].strip()
                index[video_id] = title
        except Exception:
            pass
    return index


# ---------------------------------------------------------------------------
# 2. Build finding_id -> finding text index from all findings sources
# ---------------------------------------------------------------------------

def _load_json(path: str) -> list | dict | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def build_finding_index() -> dict[str, dict]:
    """Return {finding_id: {text, quote, ...}} from all findings sources."""
    index: dict[str, dict] = {}

    # Pattern groups and their globs
    patterns = [
        str(COVERAGE_DIR / "ch*_findings_batch_*.json"),
        str(COVERAGE_DIR / "ch*_findings_repop.json"),
        str(COVERAGE_DIR / "bouncing_findings.json"),
        str(COVERAGE_DIR / "all_new_arguments.json"),
        str(COVERAGE_DIR / "alexandria_reextraction.json"),
    ]

    for pattern in patterns:
        for path in glob.glob(pattern):
            data = _load_json(path)
            if not data:
                continue
            if isinstance(data, dict):
                # Some files might be dict-wrapped; try common keys
                if "findings" in data:
                    data = data["findings"]
                else:
                    continue
            if not isinstance(data, list):
                continue
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                fid = entry.get("finding_id")
                if fid:
                    # Don't overwrite if we already have it (first source wins)
                    if fid not in index:
                        index[fid] = entry
    return index


# ---------------------------------------------------------------------------
# 3. Extract chapter number from verdict filename
# ---------------------------------------------------------------------------

_CH_RE = re.compile(r"ch(\d+)")


def extract_chapter(filename: str) -> int | None:
    m = _CH_RE.search(filename)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# 4. Collect all RESEARCH verdicts from step2 verdict files
# ---------------------------------------------------------------------------

def collect_research_verdicts() -> list[dict]:
    """Return list of {finding_id, verdict, target_section, justification,
    embed_note, chapter, source_file}."""
    results: list[dict] = []

    for path in sorted(glob.glob(str(STEP2_DIR / "*_verdicts.json"))):
        data = _load_json(path)
        if data is None:
            continue

        filename = os.path.basename(path)
        chapter = extract_chapter(filename)

        # Normalise into a list of verdict entries
        entries: list[dict] = []
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            # Could be {"verdicts": [...]} or other wrapper
            if "verdicts" in data and isinstance(data["verdicts"], list):
                entries = data["verdicts"]
            else:
                # Single verdict entry at top level
                entries = [data]

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if entry.get("verdict") != "RESEARCH":
                continue

            # Some entries carry their own chapter field
            ch = chapter
            if ch is None and "chapter" in entry:
                raw_ch = entry["chapter"]
                if isinstance(raw_ch, str):
                    m = _CH_RE.search(raw_ch)
                    ch = int(m.group(1)) if m else None
                elif isinstance(raw_ch, int):
                    ch = raw_ch

            results.append({
                "finding_id": entry.get("finding_id", ""),
                "target_section": entry.get("target_section", ""),
                "justification": entry.get("justification", ""),
                "embed_note": entry.get("embed_note"),
                "chapter": ch,
                "source_file": filename,
            })

    return results


# ---------------------------------------------------------------------------
# 5. Resolve video_id from finding_id
# ---------------------------------------------------------------------------

def video_id_from_finding(finding_id: str) -> str:
    """finding_id format: {video_id}_{number}.  Extract video_id."""
    # The video_id itself can contain underscores and hyphens.
    # The number suffix is always the last _N component.
    idx = finding_id.rfind("_")
    if idx == -1:
        return finding_id
    suffix = finding_id[idx + 1:]
    if suffix.isdigit():
        return finding_id[:idx]
    return finding_id


# ---------------------------------------------------------------------------
# 6. Deduplicate: same finding_id may appear in multiple verdict files.
#    Keep the first occurrence (by sorted filename order).
# ---------------------------------------------------------------------------

def deduplicate(verdicts: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for v in verdicts:
        fid = v["finding_id"]
        if fid in seen:
            continue
        seen.add(fid)
        out.append(v)
    return out


# ---------------------------------------------------------------------------
# 7. Generate HTML
# ---------------------------------------------------------------------------

def esc(text: str | None) -> str:
    if text is None:
        return ""
    return html.escape(str(text))


def build_html(
    verdicts: list[dict],
    finding_index: dict[str, dict],
    title_index: dict[str, str],
) -> str:
    # Group by chapter
    by_chapter: dict[int, list[dict]] = defaultdict(list)
    unknown_chapter: list[dict] = []
    for v in verdicts:
        ch = v["chapter"]
        if ch is not None:
            by_chapter[ch].append(v)
        else:
            unknown_chapter.append(v)

    # Sort within each chapter by finding_id
    for ch in by_chapter:
        by_chapter[ch].sort(key=lambda v: v["finding_id"])
    unknown_chapter.sort(key=lambda v: v["finding_id"])

    total = len(verdicts)
    chapters_sorted = sorted(by_chapter.keys())

    lines: list[str] = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html><head>")
    lines.append('<meta charset="utf-8">')
    lines.append("<title>RESEARCH Findings Review</title>")
    lines.append("<style>")
    lines.append(
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', "
        "sans-serif; max-width: 1400px; margin: 0 auto; padding: 20px; "
        "background: #f5f5f5; }"
    )
    lines.append(
        "h1 { color: #333; border-bottom: 2px solid #e67e22; "
        "padding-bottom: 10px; }"
    )
    lines.append(
        "h2 { color: #555; margin-top: 40px; border-bottom: 1px solid #ccc; }"
    )
    lines.append(
        ".stats { background: #fff; padding: 15px 20px; border-radius: 8px; "
        "margin: 20px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }"
    )
    lines.append(".stats table { border-collapse: collapse; }")
    lines.append(
        ".stats td, .stats th { padding: 6px 16px; text-align: left; }"
    )
    lines.append(
        ".finding { background: #fff; border-radius: 8px; "
        "padding: 16px 20px; margin: 12px 0; "
        "box-shadow: 0 1px 3px rgba(0,0,0,0.1); "
        "border-left: 4px solid #e67e22; }"
    )
    lines.append(
        ".finding-id { font-family: monospace; font-weight: bold; "
        "color: #e67e22; }"
    )
    lines.append(
        ".source { color: #888; font-size: 0.9em; margin: 4px 0; }"
    )
    lines.append(
        ".target-section { margin: 8px 0; padding: 8px 10px; "
        "background: #fdebd0; border-radius: 4px; font-size: 0.95em; "
        "font-weight: bold; color: #784212; }"
    )
    lines.append(
        ".finding-text { margin: 8px 0; padding: 10px; "
        "background: #fef5e7; border-radius: 4px; font-size: 0.95em; "
        "line-height: 1.5; }"
    )
    lines.append(
        ".justification { margin: 8px 0; padding: 10px; "
        "background: #fdebd0; border-radius: 4px; font-size: 0.95em; "
        "line-height: 1.5; }"
    )
    lines.append(".justification strong { color: #a04000; }")
    lines.append(
        ".no-text { color: #999; font-style: italic; }"
    )
    lines.append("</style>")
    lines.append("</head><body>")
    lines.append("")

    # Title
    lines.append(f"<h1>RESEARCH Findings ({total} total)</h1>")

    # Summary table
    lines.append("<div class='stats'><table>")
    lines.append("<tr><th>Chapter</th><th>Count</th></tr>")
    for ch in chapters_sorted:
        count = len(by_chapter[ch])
        lines.append(
            f"<tr><td><a href='#ch{ch}'>Chapter {ch}</a></td>"
            f"<td>{count}</td></tr>"
        )
    if unknown_chapter:
        lines.append(
            f"<tr><td><a href='#unknown'>Unknown chapter</a></td>"
            f"<td>{len(unknown_chapter)}</td></tr>"
        )
    lines.append("</table></div>")

    # Render each chapter group
    def render_finding(v: dict) -> None:
        fid = v["finding_id"]
        vid = video_id_from_finding(fid)
        title = title_index.get(vid, vid)
        finding = finding_index.get(fid, {})
        text = finding.get("text", "")
        target = v.get("target_section", "")
        justification = v.get("justification", "")

        lines.append("<div class='finding'>")
        lines.append(f"<span class='finding-id'>{esc(fid)}</span>")
        lines.append(f"<div class='source'>Source: {esc(title)}</div>")
        if target:
            lines.append(
                f"<div class='target-section'>Target: {esc(target)}</div>"
            )
        if text:
            lines.append(
                f"<div class='finding-text'>{esc(text)}</div>"
            )
        else:
            lines.append(
                "<div class='finding-text no-text'>"
                "[Finding text not found in findings files]</div>"
            )
        if justification:
            lines.append(
                f"<div class='justification'><strong>Research needed:"
                f"</strong> {esc(justification)}</div>"
            )
        lines.append("</div>")

    for ch in chapters_sorted:
        count = len(by_chapter[ch])
        lines.append(
            f"<h2 id='ch{ch}'>Chapter {ch} ({count} findings)</h2>"
        )
        for v in by_chapter[ch]:
            render_finding(v)

    if unknown_chapter:
        lines.append(
            f"<h2 id='unknown'>Unknown chapter "
            f"({len(unknown_chapter)} findings)</h2>"
        )
        for v in unknown_chapter:
            render_finding(v)

    lines.append("</body></html>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Building video title index...")
    title_index = build_video_title_index()
    print(f"  {len(title_index)} video titles indexed")

    print("Building finding text index...")
    finding_index = build_finding_index()
    print(f"  {len(finding_index)} findings indexed")

    print("Collecting RESEARCH verdicts from step2 batches...")
    verdicts = collect_research_verdicts()
    print(f"  {len(verdicts)} raw RESEARCH entries found")

    verdicts = deduplicate(verdicts)
    print(f"  {len(verdicts)} after deduplication")

    print("Generating HTML...")
    html_content = build_html(verdicts, finding_index, title_index)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  Written to {OUTPUT}")

    # Summary
    by_ch: dict[int | None, int] = defaultdict(int)
    missing_text = 0
    for v in verdicts:
        by_ch[v["chapter"]] += 1
        fid = v["finding_id"]
        if fid not in finding_index or not finding_index[fid].get("text"):
            missing_text += 1

    print("\n--- Summary ---")
    for ch in sorted(k for k in by_ch if k is not None):
        print(f"  Chapter {ch}: {by_ch[ch]} RESEARCH findings")
    if None in by_ch:
        print(f"  Unknown chapter: {by_ch[None]} RESEARCH findings")
    print(f"  Total: {len(verdicts)}")
    if missing_text:
        print(f"  Missing finding text: {missing_text}")


if __name__ == "__main__":
    main()
