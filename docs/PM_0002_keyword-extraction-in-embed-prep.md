# PM-0002: Keyword Extraction Reintroduced Under Renamed Concept

## Date: 2026-03-01

## What Happened

Claude implemented `extract_search_terms()`, `EMBED_STOP_WORDS`, `search_qa()`, `search_all_chapters()`, and automated status assignment (CLEAR / QA_FLAGGED / NEEDS_REVIEW) in `build_coverage.py --embed`. This is keyword extraction — the approach forbidden by PM-0001, reintroduced under "search terms" and "collision detection."

The command was intended as a bypass gate forcing the reviewer to read Q&A and chapter content before embed work. Instead, it replaced reading with grep and assigned automated verdicts. User caught it on first test run. Code reverted via `git restore`.

## Root Cause

Two systemic failures allowed the incident:

**1. PM-0001 produced no prevent-level action items.** PM-0001's only durable artifact was a MEMORY.md behavioral rule: "keyword extraction is forbidden." Claude scoped the rule to citation verification (PM-0001's domain) and treated embed preparation as exempt. No structural guard existed to catch or block the pattern in any domain. org.md now requires PMs to have prevent-level items (line 114), but PM-0001 predates that rule and was never retrofitted.

**2. No mechanism validates plans against known anti-patterns before implementation.** The approved plan said: "Extract search terms — distinctive proper nouns, quoted phrases, specific names." This is keyword extraction in plain English. Nobody flagged it because PM-0001 Lesson #4 ("flag the plan as flawed") is a behavioral rule with no enforcement — no file, no check, no automation backs it up.

**Underlying systemic cause:** Claude did not read PM-0001 or the MEMORY.md prohibition before implementing. The instructions exist and the prohibition is documented, but the workflow does not require reading them at the point where it matters — before designing a script that processes text. Claude's default implementation for data-preparation tools is keyword extraction (extract words → grep target → assign status). Each time it appears under a different name, and each time the existing rules would have caught it if read.

## Impact

- No code reached the repository — caught before commit.
- User time spent identifying and correcting the violation.
- Behavioral rules confirmed insufficient for this failure class; no structural prevent available — the failure is an AI behavioral pattern with no reliable code-level signature.

## Action Items

Each item classified per REVIEW_org.md: `[prevent]`, `[detect]`, `[mitigate-this-incident]`, `[reduce-future-blast-radius]`.

1. **[mitigate-this-incident]** Code reverted, JSON report deleted. *(done)*
2. **[detect]** MEMORY.md prohibition broadened from citation-verification-specific to universal, and placed at the top of the absolute rules section so it is read at session start. *(done)* — The prohibition existed before this incident but was scoped too narrowly. Broadening it is detect-level: it requires the AI to read and apply the rule.
3. **[prevent]** Require prevent-level action items in all PMs. *(done — classification standard added to org.md and REVIEW_org.md)* — Prevents the meta-problem: PM-0001 produced no prevent items, which allowed recurrence. No structural prevent exists for keyword extraction itself — the failure is an AI behavioral pattern that renames itself each time, and no code-level guard can distinguish it from legitimate text processing. The best available defense is ensuring the AI reads and applies existing instructions before implementing.
