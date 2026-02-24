#!/usr/bin/env python3
"""
review_extractions.py — Generate an interactive HTML report for triaging
Alexandria extraction findings from YouTube sources.

Parses all extraction files in sources/youtube/{channel}/{video_id}.txt,
extracts individual findings, cross-references them against the actual
chapter .tex files to detect already-covered topics, and generates an
interactive HTML report with pre-screened verdicts.

Usage:
    poetry run python scripts/review_extractions.py
    open sources/extraction_review.html
"""

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = PROJECT_ROOT / "sources"
YOUTUBE_DIR = SOURCES_DIR / "youtube"
OUTPUT_PATH = SOURCES_DIR / "extraction_review.html"
SEMANTIC_VERDICTS_PATH = SOURCES_DIR / "semantic_verdicts.json"
TRIAGE_VERDICTS_PATH = SOURCES_DIR / "triage_verdicts.json"

@dataclass
class Finding:
    video_title: str
    channel: str
    url: str
    extracted_date: str
    model: str
    chapter_raw: str
    chapter_nums: list
    chapter_title: str
    status: str
    description: str
    quote: str
    file_path: str
    finding_id: str
    coverage: str = ""         # "covered", "partial", or "" (from semantic review)
    triage: str = ""           # "add", "research", "not-relevant", "speculative" (for new findings)


def parse_chapter_nums(heading: str) -> list:
    """Extract chapter numbers from a chapter heading line."""
    nums = []
    for m in re.finditer(r'(\d+)\s*[-–]\s*(\d+)', heading):
        start, end = int(m.group(1)), int(m.group(2))
        nums.extend(range(start, end + 1))

    if not nums:
        for m in re.finditer(r'\d+', heading):
            nums.append(int(m.group()))

    return sorted(set(nums)) if nums else [0]


def parse_chapter_title(heading: str) -> str:
    """Extract the title part from a chapter heading."""
    for sep in [':', '\u2014', '\u2013']:
        if sep in heading:
            return heading.split(sep, 1)[1].strip()
    return heading.strip()


def parse_extraction_file(filepath: Path) -> list:
    """Parse a single extraction file into Finding objects."""
    text = filepath.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")

    meta = {}
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("# Video:"):
            meta["video_title"] = line[len("# Video:"):].strip()
        elif line.startswith("# Channel:"):
            meta["channel"] = line[len("# Channel:"):].strip()
        elif line.startswith("# URL:"):
            meta["url"] = line[len("# URL:"):].strip()
        elif line.startswith("# Extracted:"):
            meta["extracted_date"] = line[len("# Extracted:"):].strip()
        elif line.startswith("# Model:"):
            meta["model"] = line[len("# Model:"):].strip()
        elif line.startswith("## "):
            body_start = i
            break

    if not meta.get("video_title"):
        return []

    video_id = filepath.stem
    findings = []
    finding_idx = 0

    current_chapter_raw = ""
    current_chapter_nums = [0]
    current_chapter_title = ""

    i = body_start
    while i < len(lines):
        line = lines[i]

        if line.startswith("## "):
            current_chapter_raw = line
            current_chapter_nums = parse_chapter_nums(line)
            current_chapter_title = parse_chapter_title(line)
            i += 1
            continue

        if line.strip() == "---" or line.strip() == "":
            i += 1
            continue

        status_match = re.match(r'^\[([A-Z_]+)\]\s*(.*)', line)
        if status_match:
            status = status_match.group(1)
            description = status_match.group(2)

            i += 1
            while (i < len(lines) and lines[i].strip()
                   and not lines[i].startswith(">")
                   and not lines[i].startswith("## ")
                   and not re.match(r'^\[[A-Z_]+\]', lines[i])
                   and lines[i].strip() != "---"):
                description += " " + lines[i].strip()
                i += 1

            while i < len(lines) and lines[i].strip() == "":
                i += 1

            quote_lines = []
            while i < len(lines) and lines[i].startswith(">"):
                q = lines[i]
                if q.startswith("> "):
                    q = q[2:]
                elif q.startswith(">"):
                    q = q[1:]
                quote_lines.append(q)
                i += 1

            quote = "\n".join(quote_lines).strip()
            if quote.startswith('"') and quote.endswith('"'):
                quote = quote[1:-1]

            finding_id = f"{video_id}_{finding_idx}"
            finding_idx += 1
            rel_path = str(filepath.relative_to(PROJECT_ROOT))

            findings.append(Finding(
                video_title=meta.get("video_title", ""),
                channel=meta.get("channel", ""),
                url=meta.get("url", ""),
                extracted_date=meta.get("extracted_date", ""),
                model=meta.get("model", ""),
                chapter_raw=current_chapter_raw,
                chapter_nums=current_chapter_nums,
                chapter_title=current_chapter_title,
                status=status,
                description=description.strip(),
                quote=quote,
                file_path=rel_path,
                finding_id=finding_id,
            ))
            continue

        i += 1

    return findings


def parse_all_extractions() -> list:
    """Parse all extraction files and return list of Findings."""
    all_findings = []
    if not YOUTUBE_DIR.exists():
        print(f"ERROR: {YOUTUBE_DIR} does not exist")
        return []

    files = sorted(YOUTUBE_DIR.glob("*/*.txt"))
    for f in files:
        findings = parse_extraction_file(f)
        all_findings.extend(findings)

    return all_findings


def generate_html(findings: list) -> int:
    """Generate the interactive HTML review report."""

    channels = sorted(set(f.channel for f in findings))
    statuses = sorted(set(f.status for f in findings))
    all_chapter_nums = sorted(set(
        n for f in findings for n in f.chapter_nums if n > 0
    ))

    channel_counts = {}
    for f in findings:
        channel_counts[f.channel] = channel_counts.get(f.channel, 0) + 1

    status_counts = {}
    for f in findings:
        status_counts[f.status] = status_counts.get(f.status, 0) + 1

    chapter_counts = {}
    for f in findings:
        for n in f.chapter_nums:
            if n > 0:
                chapter_counts[n] = chapter_counts.get(n, 0) + 1

    coverage_counts = {"covered": 0, "partial": 0, "new": 0}
    triage_counts = {"add": 0, "research": 0, "not-relevant": 0, "speculative": 0, "none": 0}
    for f in findings:
        if f.coverage == "covered":
            coverage_counts["covered"] += 1
        elif f.coverage == "partial":
            coverage_counts["partial"] += 1
        else:
            coverage_counts["new"] += 1
        if f.triage:
            triage_counts[f.triage] = triage_counts.get(f.triage, 0) + 1
        else:
            triage_counts["none"] += 1

    status_colors = {
        "STRENGTHENS": "#059669",
        "NEW": "#2563eb",
        "WEAKENS": "#d97706",
        "UNRELATED": "#6b7280",
        "CONTEXT": "#7c3aed",
        "KNOWN": "#0891b2",
    }

    # Build cards
    cards = []
    for i, f in enumerate(findings):
        badge_color = status_colors.get(f.status, "#6b7280")

        ch_display = ", ".join(f"Ch{n}" for n in f.chapter_nums if n > 0)
        if not ch_display:
            ch_display = "General"

        ch_data = " ".join(str(n) for n in f.chapter_nums)

        desc_html = html.escape(f.description)
        quote_html = html.escape(f.quote) if f.quote else "<em>No quote</em>"
        title_html = html.escape(f.video_title)
        channel_html = html.escape(f.channel)

        # Coverage indicator (from semantic LLM review)
        if f.coverage == "covered":
            coverage_badge = '<span class="coverage-badge covered">IN BOOK</span>'
            default_verdict = "included"
            coverage_data = "covered"
        elif f.coverage == "partial":
            coverage_badge = '<span class="coverage-badge partial">PARTIAL</span>'
            default_verdict = ""
            coverage_data = "partial"
        else:
            coverage_badge = '<span class="coverage-badge new-badge">NEW</span>'
            default_verdict = ""
            coverage_data = "new"

        # Triage indicator (for new findings only)
        triage_data = f.triage or "none"
        triage_badge = ""
        triage_labels = {
            "add": ("ADD", "#16a34a", "#dcfce7"),
            "research": ("RESEARCH", "#d97706", "#fef3c7"),
            "not-relevant": ("SKIP", "#6b7280", "#f3f4f6"),
            "speculative": ("SPECULATIVE", "#dc2626", "#fef2f2"),
        }
        if f.triage in triage_labels:
            label, color, bg = triage_labels[f.triage]
            triage_badge = f'<span class="triage-badge" style="background:{bg};color:{color};border:1px solid {color}">{label}</span>'
            # Pre-set verdict based on triage
            if f.triage == "not-relevant" and not default_verdict:
                default_verdict = "not-relevant"
            elif f.triage == "speculative" and not default_verdict:
                default_verdict = "rejected"
            elif f.triage == "research" and not default_verdict:
                default_verdict = "research"
            elif f.triage == "add" and not default_verdict:
                default_verdict = "add"

        # Pre-select verdict dropdown
        verdict_options = [
            ("", "--"),
            ("included", "Already included"),
            ("add", "Need to add"),
            ("partial", "Partial addition"),
            ("research", "Research further"),
            ("rejected", "Rejected"),
            ("not-relevant", "Not relevant"),
        ]
        options_html = ""
        for val, label in verdict_options:
            selected = ' selected' if val == default_verdict else ''
            options_html += f'<option value="{val}"{selected}>{label}</option>'

        cards.append(f"""
    <div class="finding-card" data-id="{html.escape(f.finding_id)}" data-channel="{html.escape(f.channel)}" data-chapters="{ch_data}" data-status="{html.escape(f.status)}" data-verdict="{default_verdict}" data-coverage="{coverage_data}" data-triage="{triage_data}">
      <div class="card-header">
        <span class="channel-badge">{channel_html}</span>
        <a class="video-link" href="{html.escape(f.url)}" target="_blank">{title_html}</a>
        <span class="chapter-badge">{ch_display}</span>
        <span class="status-badge" style="background:{badge_color}">{html.escape(f.status)}</span>
        {coverage_badge}
        {triage_badge}
      </div>
      <div class="card-body">
        <div class="description">{desc_html}</div>
        {f'<blockquote class="quote">{quote_html}</blockquote>' if f.quote else ''}
      </div>
      <div class="card-footer">
        <select class="verdict-select" data-finding="{html.escape(f.finding_id)}">
          {options_html}
        </select>
        <textarea class="notes-input" data-finding="{html.escape(f.finding_id)}" rows="1" placeholder="Notes..."></textarea>
        <small class="file-ref">{html.escape(f.file_path)}</small>
      </div>
    </div>""")

    all_cards = "\n".join(cards)

    # Filter buttons
    channel_buttons = f'<button class="filter-btn active" data-filter="channel" data-value="all">All ({len(findings)})</button>\n'
    for ch in channels:
        channel_buttons += f'        <button class="filter-btn" data-filter="channel" data-value="{html.escape(ch)}">{html.escape(ch)} ({channel_counts[ch]})</button>\n'

    chapter_buttons = '<button class="filter-btn active" data-filter="chapter" data-value="all">All</button>\n'
    for n in all_chapter_nums:
        chapter_buttons += f'        <button class="filter-btn" data-filter="chapter" data-value="{n}">Ch{n} ({chapter_counts.get(n, 0)})</button>\n'

    status_buttons = '<button class="filter-btn active" data-filter="status" data-value="all">All</button>\n'
    for s in statuses:
        s_color = status_colors.get(s, "#6b7280")
        status_buttons += f'        <button class="filter-btn" data-filter="status" data-value="{html.escape(s)}" style="border-color:{s_color}">{html.escape(s)} ({status_counts[s]})</button>\n'

    verdict_buttons = """<button class="filter-btn active" data-filter="verdict" data-value="all">All</button>
        <button class="filter-btn" data-filter="verdict" data-value="unreviewed">Unreviewed</button>
        <button class="filter-btn" data-filter="verdict" data-value="included">Included</button>
        <button class="filter-btn" data-filter="verdict" data-value="add">Add</button>
        <button class="filter-btn" data-filter="verdict" data-value="partial">Partial</button>
        <button class="filter-btn" data-filter="verdict" data-value="research">Research</button>
        <button class="filter-btn" data-filter="verdict" data-value="rejected">Rejected</button>
        <button class="filter-btn" data-filter="verdict" data-value="not-relevant">Not relevant</button>
"""

    coverage_buttons = f"""<button class="filter-btn active" data-filter="coverage" data-value="all">All</button>
        <button class="filter-btn" data-filter="coverage" data-value="new">Not in book ({coverage_counts["new"]})</button>
        <button class="filter-btn" data-filter="coverage" data-value="partial">Partial ({coverage_counts["partial"]})</button>
        <button class="filter-btn" data-filter="coverage" data-value="covered">In book ({coverage_counts["covered"]})</button>
"""

    triage_buttons = f"""<button class="filter-btn active" data-filter="triage" data-value="all">All</button>
        <button class="filter-btn" data-filter="triage" data-value="add" style="border-color:#16a34a">Add ({triage_counts.get("add", 0)})</button>
        <button class="filter-btn" data-filter="triage" data-value="research" style="border-color:#d97706">Research ({triage_counts.get("research", 0)})</button>
        <button class="filter-btn" data-filter="triage" data-value="not-relevant" style="border-color:#6b7280">Skip ({triage_counts.get("not-relevant", 0)})</button>
        <button class="filter-btn" data-filter="triage" data-value="speculative" style="border-color:#dc2626">Speculative ({triage_counts.get("speculative", 0)})</button>
        <button class="filter-btn" data-filter="triage" data-value="none">No triage ({triage_counts.get("none", 0)})</button>
"""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Alexandria Extraction Review</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 14px; background: #f1f5f9; padding: 16px; color: #1e293b; }}
  h1 {{ font-size: 22px; margin-bottom: 8px; }}

  .top-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
  .top-bar-actions {{ display: flex; gap: 8px; }}
  .top-bar-actions button {{ padding: 6px 14px; border: 1px solid #94a3b8; border-radius: 6px; cursor: pointer; background: white; font-size: 13px; }}
  .top-bar-actions button:hover {{ background: #f8fafc; }}

  .summary {{ margin-bottom: 16px; padding: 14px 18px; background: white; border-radius: 8px; border: 1px solid #e2e8f0; display: flex; flex-wrap: wrap; gap: 20px; }}
  .summary .stat {{ display: flex; flex-direction: column; }}
  .summary .stat-value {{ font-size: 22px; font-weight: 700; }}
  .summary .stat-label {{ font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }}

  .search-bar {{ margin-bottom: 12px; }}
  .search-bar input {{ width: 100%; padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; }}
  .search-bar input:focus {{ outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }}

  .filter-section {{ margin-bottom: 10px; padding: 10px 14px; background: white; border-radius: 8px; border: 1px solid #e2e8f0; }}
  .filter-section label {{ font-weight: 600; font-size: 12px; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-right: 8px; }}
  .filter-btn {{ padding: 4px 10px; margin: 2px 3px; border: 1px solid #cbd5e1; border-radius: 4px; cursor: pointer; background: white; font-size: 12px; }}
  .filter-btn:hover {{ background: #f1f5f9; }}
  .filter-btn.active {{ background: #1e293b; color: white; border-color: #1e293b; }}

  .cards-container {{ display: flex; flex-direction: column; gap: 8px; }}
  .finding-card {{ background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; transition: border-color 0.15s; }}
  .finding-card:hover {{ border-color: #94a3b8; }}
  .finding-card.hidden {{ display: none; }}

  .finding-card[data-verdict="included"] {{ border-left: 4px solid #059669; }}
  .finding-card[data-verdict="add"] {{ border-left: 4px solid #2563eb; }}
  .finding-card[data-verdict="partial"] {{ border-left: 4px solid #eab308; }}
  .finding-card[data-verdict="research"] {{ border-left: 4px solid #d97706; }}
  .finding-card[data-verdict="rejected"] {{ border-left: 4px solid #dc2626; }}
  .finding-card[data-verdict="not-relevant"] {{ border-left: 4px solid #94a3b8; }}

  .card-header {{ padding: 10px 14px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .channel-badge {{ background: #1e293b; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
  .video-link {{ color: #2563eb; text-decoration: none; font-size: 13px; font-weight: 500; }}
  .video-link:hover {{ text-decoration: underline; }}
  .chapter-badge {{ background: #e2e8f0; color: #475569; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
  .status-badge {{ color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 700; }}

  .coverage-badge {{ padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }}
  .coverage-badge.covered {{ background: #dcfce7; color: #166534; border: 1px solid #86efac; }}
  .coverage-badge.partial {{ background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }}
  .coverage-badge.new-badge {{ background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }}

  .triage-badge {{ padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }}

  .card-body {{ padding: 12px 14px; }}
  .description {{ font-size: 13px; line-height: 1.6; color: #334155; }}
  .quote {{ margin-top: 8px; padding: 8px 12px; background: #fffbeb; border-left: 3px solid #f59e0b; font-size: 12px; line-height: 1.5; color: #92400e; font-style: italic; white-space: pre-wrap; }}
  .card-footer {{ padding: 8px 14px; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
  .verdict-select {{ padding: 4px 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 12px; }}
  .notes-input {{ flex: 1; min-width: 200px; padding: 4px 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 12px; resize: vertical; }}
  .file-ref {{ color: #94a3b8; font-size: 11px; margin-left: auto; }}

  .visible-count {{ margin-bottom: 8px; font-size: 13px; color: #64748b; }}
  #import-file {{ display: none; }}

  /* Dim covered cards slightly so uncovered stand out */
  .finding-card[data-coverage="covered"] {{ opacity: 0.7; }}
  .finding-card[data-coverage="covered"]:hover {{ opacity: 1; }}
</style>
</head>
<body>

<div class="top-bar">
  <h1>Alexandria Extraction Review</h1>
  <div class="top-bar-actions">
    <button onclick="exportVerdicts()">Export Verdicts (JSON)</button>
    <button onclick="document.getElementById('import-file').click()">Import Verdicts</button>
    <input type="file" id="import-file" accept=".json" onchange="importVerdicts(event)">
  </div>
</div>

<div class="summary" id="summary">
  <div class="stat">
    <span class="stat-value">{len(findings)}</span>
    <span class="stat-label">Total Findings</span>
  </div>
  <div class="stat">
    <span class="stat-value" style="color:#059669">{coverage_counts["covered"]}</span>
    <span class="stat-label">Likely in book</span>
  </div>
  <div class="stat">
    <span class="stat-value" style="color:#d97706">{coverage_counts["partial"]}</span>
    <span class="stat-label">Partial</span>
  </div>
  <div class="stat">
    <span class="stat-value" style="color:#2563eb">{coverage_counts["new"]}</span>
    <span class="stat-label">Not detected</span>
  </div>
  <div class="stat" style="border-left:2px solid #e2e8f0;padding-left:16px">
    <span class="stat-value" style="color:#16a34a">{triage_counts.get("add", 0)}</span>
    <span class="stat-label">Triage: Add</span>
  </div>
  <div class="stat">
    <span class="stat-value" style="color:#d97706">{triage_counts.get("research", 0)}</span>
    <span class="stat-label">Triage: Research</span>
  </div>
  <div class="stat">
    <span class="stat-value" style="color:#6b7280">{triage_counts.get("not-relevant", 0) + triage_counts.get("speculative", 0)}</span>
    <span class="stat-label">Triage: Skip</span>
  </div>
  <div class="stat">
    <span class="stat-value" id="stat-reviewed">0</span>
    <span class="stat-label">Human-reviewed</span>
  </div>
  {" ".join(f'<div class="stat"><span class="stat-value">{channel_counts[ch]}</span><span class="stat-label">{html.escape(ch)}</span></div>' for ch in channels)}
</div>

<div class="search-bar">
  <input type="text" id="search-input" placeholder="Search descriptions and quotes...">
</div>

<div class="filter-section">
  <label>Coverage:</label>
  {coverage_buttons}
</div>

<div class="filter-section">
  <label>Triage:</label>
  {triage_buttons}
</div>

<div class="filter-section">
  <label>Channel:</label>
  {channel_buttons}
</div>

<div class="filter-section">
  <label>Chapter:</label>
  {chapter_buttons}
</div>

<div class="filter-section">
  <label>Status:</label>
  {status_buttons}
</div>

<div class="filter-section">
  <label>Verdict:</label>
  {verdict_buttons}
</div>

<div class="visible-count" id="visible-count">Showing {len(findings)} of {len(findings)} findings</div>

<div class="cards-container" id="cards-container">
{all_cards}
</div>

<script>
const STORAGE_KEY = 'extraction_review_verdicts';
const totalFindings = {len(findings)};

const filterState = {{
  channel: 'all',
  chapter: 'all',
  status: 'all',
  verdict: 'all',
  coverage: 'all',
  triage: 'all',
  search: ''
}};

document.querySelectorAll('.filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    const filterType = btn.dataset.filter;
    btn.closest('.filter-section').querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterState[filterType] = btn.dataset.value;
    applyFilters();
  }});
}});

document.getElementById('search-input').addEventListener('input', (e) => {{
  filterState.search = e.target.value.toLowerCase();
  applyFilters();
}});

function applyFilters() {{
  const cards = document.querySelectorAll('.finding-card');
  let visible = 0;

  cards.forEach(card => {{
    let show = true;

    if (filterState.channel !== 'all' && card.dataset.channel !== filterState.channel) show = false;

    if (show && filterState.chapter !== 'all') {{
      const chapters = card.dataset.chapters.split(' ');
      if (!chapters.includes(filterState.chapter)) show = false;
    }}

    if (show && filterState.status !== 'all' && card.dataset.status !== filterState.status) show = false;

    if (show && filterState.coverage !== 'all' && card.dataset.coverage !== filterState.coverage) show = false;

    if (show && filterState.triage !== 'all' && card.dataset.triage !== filterState.triage) show = false;

    if (show && filterState.verdict !== 'all') {{
      const v = card.dataset.verdict || '';
      if (filterState.verdict === 'unreviewed') {{
        if (v !== '') show = false;
      }} else {{
        if (v !== filterState.verdict) show = false;
      }}
    }}

    if (show && filterState.search) {{
      const text = [
        card.querySelector('.description')?.textContent || '',
        card.querySelector('.quote')?.textContent || '',
        card.querySelector('.video-link')?.textContent || ''
      ].join(' ').toLowerCase();
      if (!text.includes(filterState.search)) show = false;
    }}

    card.classList.toggle('hidden', !show);
    if (show) visible++;
  }});

  document.getElementById('visible-count').textContent = `Showing ${{visible}} of ${{totalFindings}} findings`;
}}

document.querySelectorAll('.verdict-select').forEach(sel => {{
  sel.addEventListener('change', () => {{
    const card = sel.closest('.finding-card');
    card.dataset.verdict = sel.value;
    saveToLocalStorage();
    updateStats();
  }});
}});

document.querySelectorAll('.notes-input').forEach(ta => {{
  ta.addEventListener('input', () => {{ saveToLocalStorage(); }});
}});

function updateStats() {{
  let humanReviewed = 0;
  document.querySelectorAll('.finding-card').forEach(card => {{
    // Count as human-reviewed if the user changed from the auto-suggested default
    const sel = card.querySelector('.verdict-select');
    if (card.dataset.humanReviewed === 'true') humanReviewed++;
    else if (sel.value && !card.dataset.autoVerdict) humanReviewed++;
  }});
  document.getElementById('stat-reviewed').textContent = humanReviewed;
}}

// Track human vs auto verdicts
document.querySelectorAll('.finding-card').forEach(card => {{
  const sel = card.querySelector('.verdict-select');
  card.dataset.autoVerdict = sel.value || '';
  sel.addEventListener('change', () => {{
    if (sel.value !== card.dataset.autoVerdict) {{
      card.dataset.humanReviewed = 'true';
    }} else {{
      card.dataset.humanReviewed = '';
    }}
  }});
}});

function saveToLocalStorage() {{
  const data = {{}};
  document.querySelectorAll('.finding-card').forEach(card => {{
    const id = card.dataset.id;
    const sel = card.querySelector('.verdict-select');
    const notes = card.querySelector('.notes-input');
    const autoV = card.dataset.autoVerdict || '';
    // Save if user changed verdict or added notes
    if (sel.value !== autoV || notes.value) {{
      data[id] = {{
        verdict: sel.value,
        notes: notes.value,
        humanReviewed: card.dataset.humanReviewed === 'true'
      }};
    }}
  }});
  try {{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }} catch (e) {{}}
}}

function loadFromLocalStorage() {{
  try {{
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const data = JSON.parse(raw);
    applyVerdictData(data);
  }} catch (e) {{}}
}}

function applyVerdictData(data) {{
  document.querySelectorAll('.finding-card').forEach(card => {{
    const id = card.dataset.id;
    if (data[id]) {{
      const sel = card.querySelector('.verdict-select');
      const notes = card.querySelector('.notes-input');
      if (data[id].verdict !== undefined) {{
        sel.value = data[id].verdict;
        card.dataset.verdict = data[id].verdict;
      }}
      if (data[id].notes) notes.value = data[id].notes;
      if (data[id].humanReviewed) card.dataset.humanReviewed = 'true';
    }}
  }});
  updateStats();
}}

function exportVerdicts() {{
  const data = {{}};
  document.querySelectorAll('.finding-card').forEach(card => {{
    const id = card.dataset.id;
    const sel = card.querySelector('.verdict-select');
    const notes = card.querySelector('.notes-input');
    if (sel.value || notes.value) {{
      data[id] = {{
        verdict: sel.value,
        notes: notes.value,
        channel: card.dataset.channel,
        status: card.dataset.status,
        coverage: card.dataset.coverage,
        triage: card.dataset.triage
      }};
    }}
  }});
  const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'extraction_verdicts.json';
  a.click();
  URL.revokeObjectURL(url);
}}

function importVerdicts(event) {{
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {{
    try {{
      const data = JSON.parse(e.target.result);
      applyVerdictData(data);
      saveToLocalStorage();
      alert(`Imported verdicts for ${{Object.keys(data).length}} findings.`);
    }} catch (err) {{
      alert('Error parsing JSON: ' + err.message);
    }}
  }};
  reader.readAsText(file);
  event.target.value = '';
}}

loadFromLocalStorage();
updateStats();
</script>

</body>
</html>"""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(page, encoding="utf-8")
    return len(findings)


def load_semantic_verdicts() -> dict:
    """Load pre-computed semantic verdicts from JSON.

    The semantic verdicts file is generated by LLM agents that read each
    chapter and evaluate whether each finding's specific argument is already
    present. Values are: "covered", "partial", "new".
    """
    if not SEMANTIC_VERDICTS_PATH.exists():
        print(f"  WARNING: {SEMANTIC_VERDICTS_PATH} not found, no pre-screening")
        return {}
    data = json.loads(SEMANTIC_VERDICTS_PATH.read_text())
    print(f"  Loaded {len(data)} semantic verdicts")
    return data


def load_triage_verdicts() -> dict:
    """Load triage verdicts for 'new' findings.

    Triage verdicts categorize new findings by actionability:
    "add", "research", "not-relevant", "speculative".
    """
    if not TRIAGE_VERDICTS_PATH.exists():
        print(f"  WARNING: {TRIAGE_VERDICTS_PATH} not found, no triage data")
        return {}
    data = json.loads(TRIAGE_VERDICTS_PATH.read_text())
    print(f"  Loaded {len(data)} triage verdicts")
    return data


def main():
    print("Parsing extraction files...")
    findings = parse_all_extractions()
    print(f"  Found {len(findings)} findings from {len(set(f.file_path for f in findings))} files")

    channels = set(f.channel for f in findings)
    statuses = {}
    for f in findings:
        statuses[f.status] = statuses.get(f.status, 0) + 1
    print(f"  Channels: {', '.join(sorted(channels))}")
    print(f"  Status breakdown: {statuses}")

    print("Loading semantic verdicts...")
    semantic = load_semantic_verdicts()

    covered = 0
    partial = 0
    for f in findings:
        verdict = semantic.get(f.finding_id, "")
        f.coverage = verdict if verdict in ("covered", "partial") else ""
        if f.coverage == "covered":
            covered += 1
        elif f.coverage == "partial":
            partial += 1
    new_count = len(findings) - covered - partial
    print(f"  Covered: {covered}, Partial: {partial}, New: {new_count}")

    print("Loading triage verdicts...")
    triage = load_triage_verdicts()
    triage_counts = {}
    for f in findings:
        t = triage.get(f.finding_id, "")
        if t:
            f.triage = t
            triage_counts[t] = triage_counts.get(t, 0) + 1
    if triage_counts:
        print(f"  Triage: {triage_counts}")

    print("Generating HTML review report...")
    generate_html(findings)
    print(f"\nReport written to: {OUTPUT_PATH}")
    print(f"Open with: open {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    exit(main())
