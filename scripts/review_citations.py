#!/usr/bin/env python3
"""
review_citations.py — Generate an HTML review table for manual citation checking.

For each FOUND citation, displays:
  - The manuscript claim (cleaned LaTeX)
  - The source text snippet (extended)
  - Manual verdict selector

For each modern work, displays:
  - The manuscript claim
  - LLM evaluation of the claim's accuracy

Usage:
    poetry run python scripts/review_citations.py
    open sources/citation_review.html
"""

import html
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_registry import SOURCES, MODERN
from verify_citations import (
    PROJECT_ROOT,
    SOURCES_DIR,
    extract_citations,
    extract_claim,
    find_source_files,
    normalize_ref,
    search_passage_in_text,
    Citation,
)

OUTPUT_PATH = SOURCES_DIR / "citation_review.html"


def get_all_found_citations():
    """Extract all citations, verify them, return FOUND ones with claim text."""
    tex_files = sorted(PROJECT_ROOT.glob("chapter*.tex"))
    all_citations = []
    for tex_file in tex_files:
        cites = extract_citations(tex_file)
        all_citations.extend(cites)

    results = []
    for c in all_citations:
        key = c.key
        if key not in SOURCES:
            continue
        source_info = SOURCES[key]
        if source_info["category"] == MODERN:
            continue
        if not c.passage:
            continue

        ref = normalize_ref(c.passage) if c.passage else None
        source_files = find_source_files(key, ref=ref)
        if not source_files:
            continue

        # Search with deep=True for extended snippets
        for fpath in source_files:
            text = fpath.read_text(encoding="utf-8", errors="replace")
            snippet = search_passage_in_text(text, c.passage, key, deep=True)
            if snippet:
                c.status = "FOUND"
                c.snippet = f"[{fpath.name}] {snippet}"
                break
        else:
            continue

        if c.status != "FOUND":
            continue

        # Extract manuscript claim
        tex_path = PROJECT_ROOT / c.file
        c.claim_text = extract_claim(tex_path, c.line_num)
        results.append(c)

    return results


def generate_html(citations, modern_verifications=None):
    """Generate the review HTML file."""

    # Sort by chapter file and line number
    citations.sort(key=lambda c: (c.file, c.line_num))

    rows = []
    for i, c in enumerate(citations, 1):
        passage_str = f"[{c.passage}]" if c.passage else ""
        cite_display = html.escape(f"\\cite{passage_str}{{{c.key}}}")

        claim_html = html.escape(c.claim_text[:800])
        snippet_html = html.escape(c.snippet[:2000])

        # Source title
        source_info = SOURCES.get(c.key, {})
        source_title = source_info.get("title", c.key)
        source_author = source_info.get("author", "")

        rows.append(f"""
        <tr id="row-{i}">
          <td class="cell-num">{i}</td>
          <td class="cell-cite">
            <code>{cite_display}</code><br>
            <small>{html.escape(c.file)}:{c.line_num}</small>
          </td>
          <td class="cell-source">
            <strong>{html.escape(source_title)}</strong><br>
            <small>{html.escape(source_author)}</small>
          </td>
          <td class="cell-claim">
            <div class="text-box">{claim_html}</div>
          </td>
          <td class="cell-snippet">
            <div class="text-box snippet-box">{snippet_html}</div>
          </td>
          <td class="cell-verdict">
            <select class="verdict-select" data-row="{i}">
              <option value="">--</option>
              <option value="ok">OK</option>
              <option value="suspect">Suspect</option>
              <option value="wrong-location">Wrong Location</option>
              <option value="distorted">Distorted</option>
              <option value="fabricated">Fabricated</option>
              <option value="wrong-ref">Wrong Ref</option>
            </select>
            <br>
            <textarea class="notes-input" rows="2" placeholder="Notes..."></textarea>
          </td>
        </tr>""")

    all_rows = "\n".join(rows)

    # Modern works section
    modern_section = ""
    if modern_verifications:
        modern_rows, m_confirmed, m_flagged, m_pending = generate_modern_html(modern_verifications)
        modern_all_rows = "\n".join(modern_rows)
        modern_section = f"""
<h1 style="margin-top:32px" id="modern-works">Modern Works Verification</h1>
<div class="summary">
  <span><strong>Total:</strong> {len(modern_verifications)}</span>
  <span style="color:#059669"><strong>Confirmed:</strong> {m_confirmed}</span>
  <span style="color:#d97706"><strong>Flagged:</strong> {m_flagged}</span>
  <span style="color:#6b7280"><strong>Pending:</strong> {m_pending}</span>
</div>

<div class="filter-bar" id="modern-filter-bar">
  <strong>Filter:</strong>
  <button class="active" onclick="filterModernRows('all')">All ({len(modern_verifications)})</button>
  <button onclick="filterModernRows('CONFIRMED')">Confirmed ({m_confirmed})</button>
  <button onclick="filterModernRows('FLAGGED')">Flagged ({m_flagged})</button>
  <button onclick="filterModernRows('PENDING')">Pending ({m_pending})</button>
</div>

<table id="modern-table">
<thead>
<tr>
  <th>#</th>
  <th>Work</th>
  <th>Manuscript Claim</th>
  <th>LLM Evaluation</th>
  <th>Verdict</th>
</tr>
</thead>
<tbody>
{modern_all_rows}
</tbody>
</table>
"""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Citation Review</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; background: #f9fafb; padding: 16px; }}
  h1 {{ font-size: 20px; margin-bottom: 8px; }}
  .summary {{ margin-bottom: 16px; padding: 12px; background: white; border-radius: 8px; border: 1px solid #e5e7eb; }}
  .summary span {{ margin-right: 20px; }}
  .filter-bar {{ margin-bottom: 12px; }}
  .filter-bar button {{ padding: 4px 12px; margin-right: 6px; border: 1px solid #d1d5db; border-radius: 4px; cursor: pointer; background: white; }}
  .filter-bar button.active {{ background: #3b82f6; color: white; border-color: #3b82f6; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 24px; }}
  th {{ background: #1f2937; color: white; padding: 10px 8px; text-align: left; font-size: 12px; position: sticky; top: 0; z-index: 10; }}
  td {{ padding: 8px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
  .cell-num {{ width: 30px; text-align: center; font-weight: bold; }}
  .cell-cite {{ width: 160px; }}
  .cell-source {{ width: 160px; }}
  .cell-claim {{ width: 30%; }}
  .cell-snippet {{ width: 30%; }}
  .cell-verdict {{ width: 120px; }}
  .text-box {{ max-height: 200px; overflow-y: auto; font-size: 12px; line-height: 1.5; white-space: pre-wrap; word-break: break-word; padding: 4px; border: 1px solid #e5e7eb; border-radius: 4px; background: #fafafa; }}
  .snippet-box {{ max-height: 300px; background: #fffbeb; }}
  .eval-box {{ max-height: 300px; overflow-y: auto; font-size: 12px; line-height: 1.6; padding: 8px; border: 1px solid #e5e7eb; border-radius: 4px; background: #f0fdf4; }}
  .eval-box.flagged {{ background: #fef3c7; }}
  .eval-box.pending {{ background: #f3f4f6; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; color: white; font-size: 11px; font-weight: bold; }}
  code {{ font-size: 11px; background: #f3f4f6; padding: 2px 4px; border-radius: 3px; }}
  small {{ color: #6b7280; }}
  .verdict-select {{ width: 100%; padding: 4px; margin-bottom: 4px; border: 1px solid #d1d5db; border-radius: 4px; }}
  .notes-input {{ width: 100%; padding: 4px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 11px; resize: vertical; }}
  tr.hidden {{ display: none; }}
  .section-nav {{ margin-bottom: 16px; padding: 12px; background: #1f2937; border-radius: 8px; }}
  .section-nav a {{ color: white; text-decoration: none; margin-right: 20px; font-weight: bold; }}
  .section-nav a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>

<div class="section-nav">
  <a href="#source-citations">Source Citations ({len(citations)})</a>
  <a href="#modern-works">Modern Works ({len(modern_verifications) if modern_verifications else 0})</a>
  <a href="javascript:void(0)" onclick="exportVerdicts()" style="float:right">Export All Verdicts (JSON)</a>
</div>

<h1 id="source-citations">Source Citation Review</h1>
<div class="summary">
  <span><strong>Total FOUND:</strong> {len(citations)}</span>
</div>

<table id="citation-table">
<thead>
<tr>
  <th>#</th>
  <th>Citation</th>
  <th>Source</th>
  <th>Manuscript Claim</th>
  <th>Source Text</th>
  <th>Verdict</th>
</tr>
</thead>
<tbody>
{all_rows}
</tbody>
</table>

<div>
{modern_section}
</div>

<script>
function filterModernRows(level) {{
  document.querySelectorAll('#modern-filter-bar button').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('#modern-table tbody tr').forEach(tr => {{
    if (level === 'all') {{
      tr.classList.remove('hidden');
    }} else {{
      const badge = tr.querySelector('.badge');
      if (badge && badge.textContent === level) {{
        tr.classList.remove('hidden');
      }} else {{
        tr.classList.add('hidden');
      }}
    }}
  }});
}}

function exportVerdicts() {{
  const data = [];
  document.querySelectorAll('tbody tr').forEach(tr => {{
    const sel = tr.querySelector('.verdict-select');
    const notes = tr.querySelector('.notes-input');
    const cite = tr.querySelector('code');
    const loc = tr.querySelector('small');
    if (sel && sel.value) {{
      data.push({{
        row: sel.dataset.row,
        citation: cite ? cite.textContent : '',
        location: loc ? loc.textContent : '',
        verdict: sel.value,
        notes: notes ? notes.value : ''
      }});
    }}
  }});
  const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'citation_verdicts.json';
  a.click();
  URL.revokeObjectURL(url);
}}
</script>

</body>
</html>"""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(page, encoding="utf-8")
    return len(citations)


def get_modern_verifications():
    """Load modern work verification data from JSON files."""
    modern_dir = SOURCES_DIR / "modern"
    verifications = []
    for key, info in sorted(SOURCES.items()):
        if info.get("category") != MODERN:
            continue
        safe_key = key.replace(":", "_")
        vf = modern_dir / safe_key / "verification.json"
        if vf.exists():
            verifications.append(json.loads(vf.read_text()))
    return verifications


def generate_modern_html(verifications):
    """Generate HTML rows for modern works verification section."""
    rows = []
    confirmed = 0
    flagged = 0
    pending = 0

    for i, v in enumerate(verifications, 1):
        eval_data = v.get("llm_evaluation", {})
        eval_status = eval_data.get("status", "pending")

        if eval_status == "confirmed":
            bg = "#d1fae5"
            badge_color = "#059669"
            badge_text = "CONFIRMED"
            eval_css = "eval-box"
            confirmed += 1
        elif eval_status == "flagged":
            bg = "#fef3c7"
            badge_color = "#d97706"
            badge_text = "FLAGGED"
            eval_css = "eval-box flagged"
            flagged += 1
        else:
            bg = "#f3f4f6"
            badge_color = "#6b7280"
            badge_text = "PENDING"
            eval_css = "eval-box pending"
            pending += 1

        # Manuscript claims
        claim_parts = []
        for cit in v.get("manuscript_claims", []):
            claim_clean = html.escape(cit["claim"].replace("\n", " ").strip())
            claim_parts.append(
                f'<div style="margin-bottom:6px">{claim_clean}'
                f'<br><small style="color:#6b7280">{html.escape(cit["file"])}:{cit["line"]}</small></div>'
            )
        claims_html = "".join(claim_parts)

        # LLM evaluation
        eval_text = eval_data.get("evaluation", "Not yet evaluated.")
        eval_html = html.escape(eval_text).replace("\n", "<br>")

        rows.append(f"""
        <tr id="modern-row-{i}" style="background-color: {bg}">
          <td class="cell-num">{i}</td>
          <td class="cell-cite">
            <code>{html.escape(v.get('key', ''))}</code><br>
            <strong>{html.escape(v.get('title', ''))}</strong><br>
            <small>{html.escape(v.get('author', ''))} ({html.escape(str(v.get('year', '')))})</small><br>
            <span class="badge" style="background:{badge_color}">{badge_text}</span>
          </td>
          <td class="cell-claim">
            <div class="text-box">{claims_html}</div>
          </td>
          <td class="cell-snippet">
            <div class="{eval_css}">{eval_html}</div>
          </td>
          <td class="cell-verdict">
            <select class="verdict-select" data-row="modern-{i}">
              <option value="">--</option>
              <option value="ok">OK — Confirmed</option>
              <option value="suspect">Suspect</option>
              <option value="not-real">Not a Real Work</option>
              <option value="mischaracterized">Mischaracterized</option>
            </select>
            <br>
            <textarea class="notes-input" rows="2" placeholder="Notes..."></textarea>
          </td>
        </tr>""")

    return rows, confirmed, flagged, pending


def main():
    print("Extracting and verifying citations...")
    citations = get_all_found_citations()
    print(f"  {len(citations)} FOUND citations")

    # Load modern verifications
    print("Loading modern work verifications...")
    modern_verifications = get_modern_verifications()
    print(f"  {len(modern_verifications)} modern works loaded")

    print("Generating HTML review table...")
    count = generate_html(citations, modern_verifications)
    print(f"\nReview table written to: {OUTPUT_PATH}")
    print(f"Open with: open {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
