# DD-0001: Citation Review Report for Human Verification

## The Problem

The manuscript cites ~257 ancient and modern sources. The citation pipeline can download public-domain texts and locate referenced passages by section number. But locating a passage is not the same as verifying it. The question "does the manuscript accurately represent what this source says?" requires semantic judgment that no string-matching algorithm can provide.

Previous attempts at automated verification (keyword extraction, similarity scoring) produced false confidence. See `docs/PM_0001_keyword-extraction-fake-verification.md`.

## Three-Step Process

### Step 1: Download (automated, reproducible)

```bash
poetry run python scripts/download_sources.py
```

Fetches all public-domain source texts to `sources/`. URLs are defined in `scripts/source_registry.py`. Anyone cloning the repo can run this command and get identical source texts.

Modern copyrighted works (31 citations) cannot be downloaded. The report shows their title, author, and acquisition instructions instead.

### Step 2: Extract and Present (automated)

```bash
poetry run python scripts/verify_citations.py --review
```

This does three things:
1. Extracts every `\cite` command from all chapter files
2. Locates the referenced passage in the downloaded source text (by section number, book/chapter, or fingerprint pattern)
3. Generates `sources/citation_review.html` — a side-by-side HTML report

The HTML report shows every citation as a two-column entry:
- **Left column (Manuscript):** ~15 lines of cleaned LaTeX context around the `\cite` command, showing the full argument being made
- **Right column (Source):** The actual source text around the matched passage (2000 chars for LOCATED citations), or source metadata for general references and modern works

All 257 citations appear in the report, grouped by chapter. Each entry is color-coded by status:
- **LOCATED** (green) — passage found in downloaded text, needs semantic review
- **NO_PASSAGE** (yellow) — general reference with no specific passage cited; shows source title/author
- **MODERN** (blue) — copyrighted modern work; shows title and how to obtain
- **NOT_FOUND** (red) — source downloaded but passage not located
- **NO_SOURCE** (red) — source not yet downloaded

### Step 3: Semantic Verification (human or expert LLM)

A skilled reviewer reads each side-by-side pair and judges: **does the manuscript's claim accurately represent what the source says?**

This step is NEVER automated by pattern matching, keyword extraction, or similarity scoring. It requires:
- Understanding the argument the manuscript is making (not just the sentence containing the cite)
- Understanding what the source passage actually says in context
- Judging whether the manuscript's characterization is fair and accurate

This can be done by:
- A human scholar reading the report
- A skilled LLM (e.g., Claude, ChatGPT) given the full context of both columns and asked to judge accuracy

The key distinction: an LLM reading and reasoning about both texts is real verification. A script counting keyword overlap is fake verification. The difference is whether the system understands meaning or just matches strings.

## What the script does NOT do

- No keyword extraction
- No overlap scoring or similarity metrics
- No risk levels or confidence scores
- No automated pass/fail judgment
- No AI verdicts baked into the report

The script LOCATES passages and PRESENTS them side by side. Judgment is separate.

## Status rename: FOUND -> LOCATED

"FOUND" implied verification was complete. "LOCATED" makes clear the script only found the passage — it says nothing about whether the manuscript's claim about that passage is accurate.

## CLI changes

- `--deep` (associated with abandoned keyword plan) replaced with `--review`
- `--review` generates the HTML report with 2000-char snippets and full claim context
- Without `--review`, the script still generates the compact `verification_report.md` with 300-char snippets

## Files changed

| File | Action | What |
|------|--------|------|
| `scripts/verify_citations.py` | MODIFIED | Renamed FOUND->LOCATED, `--deep`->`--review`, added HTML report generator |
| `sources/hallucination_report.md` | DELETED | Stale keyword scoring report |
| `sources/citation_review_table.md` | DELETED | Stale AI-judged verdicts |
| `sources/citation_review.html` | OUTPUT | New HTML side-by-side review report (gitignored) |
| `.gitignore` | MODIFIED | Updated for new report filename |
| `docs/DD_0001_citation-review-report.md` | CREATED | This design doc |
