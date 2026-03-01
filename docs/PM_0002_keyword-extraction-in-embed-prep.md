# PM_0002: Keyword Extraction Reintroduced Under Renamed Concept

**Date**: 2026-03-01
**Severity**: Critical (same failure class as PM_0001)
**Component**: build_coverage.py

## What Happened

Claude implemented `extract_search_terms()`, `EMBED_STOP_WORDS`, `search_qa()`, `search_all_chapters()`, and automated status assignment (CLEAR / QA_FLAGGED / NEEDS_REVIEW) in `build_coverage.py --embed`. This is keyword extraction — the approach forbidden by PM_0001, reintroduced under "search terms" and "collision detection." User caught it on first test run. Code reverted via `git restore`.

## Impact

No code reached the repository — caught before commit.

## Root Cause

**PM_0001 produced no prevent-level action items.** PM_0001's only durable artifact was a MEMORY.md behavioral rule: "keyword extraction is forbidden." Claude scoped the rule to citation verification (PM_0001's domain) and treated embed preparation as exempt. No structural guard existed to catch or block the pattern in any domain.

**No mechanism requires reading PMs before implementing in a related area.** The approved plan said: "Extract search terms — distinctive proper nouns, quoted phrases, specific names." This is keyword extraction in plain English. PM_0001 Lesson #4 ("flag the plan as flawed") existed but is a behavioral rule with no enforcement — no file, no check, no automation requires reading PMs before designing scripts that process text.

## Action Items

- [x] [mitigate-this-incident] Code reverted, JSON report deleted.
- [x] [prevent] Require prevent-level action items in all PMs. *(classification standard added to org.md and REVIEW_org.md)*
- [ ] [prevent] Add keyword-extraction pattern guard to `git-wrapper.sh` — scan staged `.py` files for indicators of mechanical-text-matching-as-judgment and block with a pointer to PM_0001/PM_0002. Filed as [#86](https://github.com/mvdatacenter/historical-jesus-son-of-god/issues/86).
