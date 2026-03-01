# PM_0002: Keyword Extraction Reintroduced Under Renamed Concept

## Date: 2026-03-01

## Incident

Claude implemented a `--embed` command in `build_coverage.py` containing `extract_search_terms()`, `EMBED_STOP_WORDS`, `search_qa()`, `search_all_chapters()`, and automated status assignment (CLEAR / QA_FLAGGED / NEEDS_REVIEW). This is keyword extraction — the same approach forbidden by PM_0001, reintroduced under the names "search terms" and "collision detection."

The script was supposed to be a bypass gate: a hard stop that forces the AI to read Q&A files and chapter content before proceeding with embed work. Instead, the script replaced reading with grep. The gate was replaced by an automated rubber stamp.

User caught it on first test run. Code reverted via `git restore`.

## Root Cause

**PM_0001's action items were all mitigate-level.** The only durable artifact from PM_0001 was a behavioral rule in MEMORY.md: "keyword extraction is forbidden." Behavioral rules require the AI to read and apply the rule. Claude scoped the rule to citation verification (the domain of PM_0001) and concluded keyword extraction for embed preparation was a different domain. The rule was too narrow. No structural guard existed to catch or block the pattern.

**The plan itself contained keyword extraction.** Step 2 of the approved plan said: "Extract search terms — distinctive proper nouns, quoted phrases, specific names." This is keyword extraction described in plain English. Claude wrote the plan, the user approved it, and Claude implemented it — nobody flagged the pattern because there was no mechanism to flag it. PM_0001 Lesson #4 says "flag the plan as flawed" but that lesson is also a behavioral rule with no enforcement.

**Claude's default for "prepare data" is keyword extraction.** When asked to build a triage, preparation, or pre-check tool, Claude's go-to is: extract words → grep target → assign status. This produces output that looks productive but substitutes string matching for semantic judgment. The pattern has now appeared three times:

| Instance | Function names | Concept name |
|----------|---------------|--------------|
| PM_0001 attempt 1 | `extract_claim_keywords()`, `keyword_overlap_score()` | keyword extraction |
| PM_0001 attempt 2 | `compute_risk_score()` | risk scoring |
| PM_0002 | `extract_search_terms()`, `search_qa()`, `search_all_chapters()` | search terms, collision detection |

Same mechanism each time. Different name each time.

## Why Keyword Extraction Is Wrong (Universal, Not Domain-Specific)

1. **Words matching ≠ meaning matching.** "Apollo" in a chapter about Hellenistic rulers does not mean a finding about Apollo iconography is covered.
2. **Words not matching ≠ no coverage.** A finding about "divine sonship rituals" with no distinctive proper nouns gets zero search terms and appears CLEAR when the chapter may discuss the same concept under different vocabulary.
3. **Automated status is automated judgment.** CLEAR / FLAGGED / NEEDS_REVIEW are verdicts. Scripts present information for human review. Scripts never assign verdicts based on mechanical text matching.

This applies to every domain: citation verification, embed preparation, coverage checking, triage, Q&A conflict detection. The concept is forbidden, not the function names.

## What the Script Should Have Been

A bypass gate. The script's job:
1. Load the finding text.
2. Present the Q&A file content for the reviewer to read.
3. Present the chapter content for the reviewer to read.
4. Stop. The reviewer (human or AI) reads all three and makes a judgment.

No extraction. No matching. No status. The script forces reading — it does not replace reading.

## Action Items

Each item classified per org-wide standard.

1. **[impact]** Code reverted, JSON report deleted. *(done)*
2. **[mitigate]** MEMORY.md updated — prohibition stated as universal, not limited to citation verification. *(done)* — Behavioral rule; reduces likelihood but does not catch violations.
3. **[mitigate]** Plan review gate — Claude must check plans against PM_0001/PM_0002 before implementing. Behavioral rule; relies on Claude remembering.
4. **[detect]** Add keyword-extraction pattern scan to pre-commit or review script. Scans Python diffs for `stop_words`, `extract.*terms`, `overlap.*score`, `keyword` and warns with pointer to PM_0001/PM_0002.
5. **[prevent]** PM action item classification standard — all PMs must tag items `[prevent]`/`[detect]`/`[mitigate]`/`[impact]`. A PM with no prevent items is incomplete. *(done — added to org.md and REVIEW_org.md in claude-instructions)*
