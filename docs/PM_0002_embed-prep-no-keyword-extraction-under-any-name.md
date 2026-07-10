# PM-0002: Keyword Extraction Reintroduced Under Renamed Concept

## What Happened

`build_coverage.py --embed` was implemented with `extract_search_terms()`, `EMBED_STOP_WORDS`, `search_qa()`, `search_all_chapters()`, and automated status assignment (`CLEAR` / `QA_FLAGGED` / `NEEDS_REVIEW`). This is the operation forbidden by PM-0001 — extract terms, grep targets, assign status — reintroduced as "search terms" and "collision detection." Caught on first test run; reverted via `git restore`.
The code stayed out of the repository, and the approved plan that specified "extract search terms — distinctive proper nouns, quoted phrases, specific names" had to be revised before reimplementation.

## Root Cause

The PM-0001 prohibition existed only as a behavioral rule in MEMORY.md. No review gate forced checking the plan or the diff against PM-0001 before implementation. The behavioral rule was scoped narrowly to citation verification; embed preparation was treated as exempt despite using the same operation.

Discipline-based prohibitions do not generalize across contexts. When the same operation is given a new name, the rule does not trigger — only a structural check against the operation itself catches recurrences.

## Action Items

- [x] [prevent] Push-to-main block and PR review gate ensure every change is reviewed against PMs before it ships; direct pushes to `main` are hard-blocked and PR branches require self-review against PMs, implemented in #96 and #91.
- [x] [prevent] The public boundary rule in `docs/REVIEW.md` keeps first-stage extraction/prep tooling and exploratory outputs outside this repo until they become public result-building code or citation material.
