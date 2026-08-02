# Citation Verification

Operator guide for the citation verification pipeline. For the full technical specification, see `docs/DD_0001_citation-review-report.md`.
For why keyword extraction is forbidden, see `docs/PM_0001_citation-verification-locate-and-present-not-score.md`.

## Three-Step Pipeline

**Step 1: Download (automated, reproducible)**

```bash
poetry run python scripts/download_sources.py
```

Fetches all public-domain source texts to `sources/`. URLs are defined in `scripts/source_registry.py`, which maps each bibliography key to one or more public-domain URLs. Modern copyrighted works cannot be downloaded — the report shows title, author, and acquisition instructions instead.

**Step 2: Extract and Present (automated)**

```bash
poetry run python scripts/verify_citations.py --review
```

Extracts every `\cite` command from chapter files, locates the referenced passage in downloaded text, and generates `sources/citation_review.html` — a side-by-side HTML report showing manuscript context alongside source text.

**Step 3: Semantic Verification (human or expert LLM)**

A reviewer reads each side-by-side pair and judges whether the manuscript's claim accurately represents what the source says. This step is never automated by pattern matching, keyword extraction, or similarity scoring.

## Citation Statuses

| Status | Meaning |
|--------|---------|
| **LOCATED** | Passage found in downloaded text; needs semantic review |
| **NO_PASSAGE** | General reference with no specific passage cited |
| **MODERN** | Copyrighted modern work; shows title and how to obtain |
| **NOT_FOUND** | Source downloaded but passage not located |
| **NO_SOURCE** | Source not yet downloaded |

## What the Pipeline Does NOT Do

- No keyword extraction or similarity scoring
- No automated pass/fail judgment or risk levels
- No AI verdicts baked into reports
- No substitution of mechanical matching for semantic judgment

The script LOCATES passages and PRESENTS them side by side. Judgment is separate.
