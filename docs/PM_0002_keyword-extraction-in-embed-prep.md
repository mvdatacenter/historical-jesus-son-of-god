# PM_0002: Keyword Extraction Reintroduced Under Renamed Concept

**Date**: 2026-03-01
**Severity**: Critical (same failure class as PM_0001)
**Component**: build_coverage.py

## What Happened

Claude implemented `extract_search_terms()`, `EMBED_STOP_WORDS`, `search_qa()`, `search_all_chapters()`, and automated status assignment (CLEAR / QA_FLAGGED / NEEDS_REVIEW) in `build_coverage.py --embed`. This is keyword extraction — the approach forbidden by PM_0001, reintroduced under "search terms" and "collision detection." User caught it on first test run. Code reverted via `git restore`.

## Impact

No code reached the repository — caught before commit.

## Root Cause

**No review process existed to catch this before it shipped.** The approved plan said: "Extract search terms — distinctive proper nouns, quoted phrases, specific names." This is keyword extraction in plain English. No review gate forced checking the plan or the diff against PM_0001 before implementation. The only guard was a MEMORY.md behavioral rule ("keyword extraction is forbidden") which Claude scoped to citation verification and treated embed preparation as exempt.

## Action Items

- [x] [mitigate-this-incident] Code reverted, JSON report deleted.
- [x] [prevent] Push-to-main block and PR review gate ensure every change is reviewed against PMs before it ships. Direct pushes to main are hard-blocked; pushes to PR branches require self-review against PMs. *(implemented in git-wrapper.sh)*
