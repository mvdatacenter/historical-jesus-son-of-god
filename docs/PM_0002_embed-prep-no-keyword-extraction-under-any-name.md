# PM-0002: Keyword Extraction Reintroduced Under Renamed Concept

## What Happened

`build_coverage.py --embed` was implemented with `extract_search_terms()`, `EMBED_STOP_WORDS`, `search_qa()`, `search_all_chapters()`, and automated status assignment (`CLEAR` / `QA_FLAGGED` / `NEEDS_REVIEW`). This is the operation forbidden by PM-0001 — extract terms, grep targets, assign status — reintroduced as "search terms" and "collision detection." Caught on first test run; reverted via `git restore`.

## Impact

- No code reached the repository
- The approved plan, which specified "extract search terms — distinctive proper nouns, quoted phrases, specific names," had to be revised before any reimplementation

## Root Cause

The PM-0001 prohibition existed only as a behavioral rule in MEMORY.md. No review gate forced checking the plan or the diff against PM-0001 before implementation. The behavioral rule was scoped narrowly to citation verification; embed preparation was treated as exempt despite using the same operation.

Discipline-based prohibitions do not generalize across contexts. When the same operation is given a new name, the rule does not trigger — only a structural check against the operation itself catches recurrences.

## Action Items

- [x] [mitigate-this-incident] Reverted code; deleted the JSON report.
- [x] [prevent] Push-to-main block and PR review gate ensure every change is reviewed against PMs before it ships. Direct pushes to `main` are hard-blocked; pushes to PR branches require self-review against PMs. *(implemented in `git-wrapper.sh`)*
- [x] [prevent] Redesigned DD-0002 Step 2 so the script injects PM-0001/PM-0002 anti-pattern rules into the AI's context as part of the embed workflow. The AI does not have to remember to read the rules — the tool puts them in front of the AI at the point of decision. *(design spec updated in DD-0002; implementation: `build_coverage.py --embed-prep`)*
