#!/usr/bin/env python3
"""
review_citations.py — Generate an HTML review table for manual hallucination checking.

For each FOUND citation, displays:
  - The manuscript claim (cleaned LaTeX)
  - The source text snippet (extended)
  - Risk score and keyword analysis
  - Color-coded rows by risk level

Usage:
    poetry run python scripts/review_citations.py
    open sources/citation_review.html
"""

import html
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
    extract_claim_keywords,
    find_source_files,
    keyword_overlap_score,
    classify_claim_type,
    normalize_ref,
    search_passage_in_text,
    snippet_quality_score,
    compute_risk_score,
    Citation,
)

OUTPUT_PATH = SOURCES_DIR / "citation_review.html"


def get_all_found_citations():
    """Extract all citations, verify them, return FOUND ones with deep data."""
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

        # Deep analysis
        tex_path = PROJECT_ROOT / c.file
        c.claim_text = extract_claim(tex_path, c.line_num)
        c.claim_keywords = extract_claim_keywords(c.claim_text)
        ref = normalize_ref(c.passage) if c.passage else {}
        total, level, breakdown, matched = compute_risk_score(c, ref)
        c.risk_score = total
        c.risk_level = level
        c.risk_breakdown = breakdown
        c.matched_keywords = matched
        results.append(c)

    return results


def truncate(text, max_len=500):
    """Truncate text to max_len chars."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def highlight_keywords(text, keywords, css_class="kw-hit"):
    """Highlight matched keywords in HTML text."""
    escaped = html.escape(text)
    for kw in sorted(keywords, key=len, reverse=True):
        pattern = re.compile(rf"\b({re.escape(html.escape(kw))})\b", re.IGNORECASE)
        escaped = pattern.sub(rf'<mark class="{css_class}">\1</mark>', escaped)
    return escaped


def generate_html(citations):
    """Generate the review HTML file."""

    # Sort: HIGH first, then MEDIUM, then LOW; within each group by score desc
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    citations.sort(key=lambda c: (order.get(c.risk_level, 9), -c.risk_score, c.file, c.line_num))

    rows = []
    for i, c in enumerate(citations, 1):
        risk_color = {
            "HIGH": "#fee2e2",    # red-100
            "MEDIUM": "#fef3c7",  # amber-100
            "LOW": "#d1fae5",     # green-100
        }.get(c.risk_level, "#f3f4f6")

        badge_color = {
            "HIGH": "#dc2626",
            "MEDIUM": "#d97706",
            "LOW": "#059669",
        }.get(c.risk_level, "#6b7280")

        passage_str = f"[{c.passage}]" if c.passage else ""
        cite_display = html.escape(f"\\cite{passage_str}{{{c.key}}}")

        # Highlight keywords in both claim and snippet
        claim_html = highlight_keywords(c.claim_text[:600], c.matched_keywords)
        snippet_html = highlight_keywords(c.snippet[:2000], c.matched_keywords, "kw-src")

        # Breakdown display
        bd = c.risk_breakdown
        breakdown_parts = []
        for factor, score in bd.items():
            label = factor.replace("_", " ").title()
            fcolor = "#059669" if score == 0 else ("#d97706" if score == 1 else "#dc2626")
            breakdown_parts.append(f'<span style="color:{fcolor}">{label}={score}</span>')
        breakdown_html = " | ".join(breakdown_parts)

        # Keywords display
        kw_total = len(c.claim_keywords)
        kw_matched = len(c.matched_keywords)
        kw_ratio = kw_matched / max(kw_total, 1)
        kw_color = "#059669" if kw_ratio >= 0.3 else ("#d97706" if kw_ratio >= 0.1 else "#dc2626")
        missed_kw = [k for k in c.claim_keywords if k not in c.matched_keywords]

        # Source title
        source_info = SOURCES.get(c.key, {})
        source_title = source_info.get("title", c.key)
        source_author = source_info.get("author", "")

        rows.append(f"""
        <tr id="row-{i}" style="background-color: {risk_color}">
          <td class="cell-num">{i}</td>
          <td class="cell-cite">
            <code>{cite_display}</code><br>
            <small>{html.escape(c.file)}:{c.line_num}</small><br>
            <span class="badge" style="background:{badge_color}">{c.risk_level}</span>
            <span class="score">Score: {c.risk_score}/8</span><br>
            <small>{breakdown_html}</small>
          </td>
          <td class="cell-source">
            <strong>{html.escape(source_title)}</strong><br>
            <small>{html.escape(source_author)}</small><br>
            <small style="color:{kw_color}">Keywords: {kw_matched}/{kw_total} matched</small><br>
            <small>Matched: <b>{html.escape(', '.join(c.matched_keywords[:15]))}</b></small><br>
            <small>Missed: {html.escape(', '.join(missed_kw[:10]))}</small>
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

    # Count by risk
    high = sum(1 for c in citations if c.risk_level == "HIGH")
    medium = sum(1 for c in citations if c.risk_level == "MEDIUM")
    low = sum(1 for c in citations if c.risk_level == "LOW")

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Citation Review — Hallucination Check</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; background: #f9fafb; padding: 16px; }}
  h1 {{ font-size: 20px; margin-bottom: 8px; }}
  .summary {{ margin-bottom: 16px; padding: 12px; background: white; border-radius: 8px; border: 1px solid #e5e7eb; }}
  .summary span {{ margin-right: 20px; }}
  .filter-bar {{ margin-bottom: 12px; }}
  .filter-bar button {{ padding: 4px 12px; margin-right: 6px; border: 1px solid #d1d5db; border-radius: 4px; cursor: pointer; background: white; }}
  .filter-bar button.active {{ background: #3b82f6; color: white; border-color: #3b82f6; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  th {{ background: #1f2937; color: white; padding: 10px 8px; text-align: left; font-size: 12px; position: sticky; top: 0; z-index: 10; }}
  td {{ padding: 8px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
  .cell-num {{ width: 30px; text-align: center; font-weight: bold; }}
  .cell-cite {{ width: 180px; }}
  .cell-source {{ width: 180px; }}
  .cell-claim {{ width: 28%; }}
  .cell-snippet {{ width: 32%; }}
  .cell-verdict {{ width: 120px; }}
  .text-box {{ max-height: 200px; overflow-y: auto; font-size: 12px; line-height: 1.5; white-space: pre-wrap; word-break: break-word; padding: 4px; border: 1px solid #e5e7eb; border-radius: 4px; background: #fafafa; }}
  .snippet-box {{ max-height: 300px; background: #fffbeb; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; color: white; font-size: 11px; font-weight: bold; }}
  .score {{ font-size: 12px; font-weight: bold; margin-left: 4px; }}
  code {{ font-size: 11px; background: #f3f4f6; padding: 2px 4px; border-radius: 3px; }}
  mark.kw-hit {{ background: #bfdbfe; padding: 0 1px; border-radius: 2px; }}
  mark.kw-src {{ background: #a7f3d0; padding: 0 1px; border-radius: 2px; }}
  small {{ color: #6b7280; }}
  .verdict-select {{ width: 100%; padding: 4px; margin-bottom: 4px; border: 1px solid #d1d5db; border-radius: 4px; }}
  .notes-input {{ width: 100%; padding: 4px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 11px; resize: vertical; }}
  tr.hidden {{ display: none; }}
  #export-btn {{ margin-left: 12px; padding: 4px 12px; background: #059669; color: white; border: none; border-radius: 4px; cursor: pointer; }}
  .expand-btn {{ cursor: pointer; font-size: 11px; color: #3b82f6; text-decoration: underline; border: none; background: none; }}
</style>
</head>
<body>

<h1>Citation Hallucination Review</h1>
<div class="summary">
  <span><strong>Total FOUND:</strong> {len(citations)}</span>
  <span style="color:#dc2626"><strong>HIGH:</strong> {high}</span>
  <span style="color:#d97706"><strong>MEDIUM:</strong> {medium}</span>
  <span style="color:#059669"><strong>LOW:</strong> {low}</span>
</div>

<div class="filter-bar">
  <strong>Filter:</strong>
  <button class="active" onclick="filterRows('all')">All ({len(citations)})</button>
  <button onclick="filterRows('HIGH')">HIGH ({high})</button>
  <button onclick="filterRows('MEDIUM')">MEDIUM ({medium})</button>
  <button onclick="filterRows('LOW')">LOW ({low})</button>
  <button id="export-btn" onclick="exportVerdicts()">Export Verdicts (JSON)</button>
</div>

<table>
<thead>
<tr>
  <th>#</th>
  <th>Citation / Risk</th>
  <th>Source / Keywords</th>
  <th>Manuscript Claim</th>
  <th>Source Text</th>
  <th>Verdict</th>
</tr>
</thead>
<tbody>
{all_rows}
</tbody>
</table>

<script>
function filterRows(level) {{
  document.querySelectorAll('.filter-bar button').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('tbody tr').forEach(tr => {{
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


def main():
    print("Extracting and verifying citations (deep mode)...")
    citations = get_all_found_citations()
    print(f"  {len(citations)} FOUND citations with deep analysis")

    high = sum(1 for c in citations if c.risk_level == "HIGH")
    medium = sum(1 for c in citations if c.risk_level == "MEDIUM")
    low = sum(1 for c in citations if c.risk_level == "LOW")
    print(f"  HIGH: {high}, MEDIUM: {medium}, LOW: {low}")

    print("Generating HTML review table...")
    count = generate_html(citations)
    print(f"\nReview table written to: {OUTPUT_PATH}")
    print(f"Open with: open {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
