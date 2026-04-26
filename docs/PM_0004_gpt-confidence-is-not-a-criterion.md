# PM-0004: GPT Verdicts Adopted as Research Filter

## What Happened

Six research findings about Greek mystery cult transmission to Church Fathers were sent to ChatGPT with the prompt: *"For each claim, give me: VERDICT: TRUE / PARTIALLY TRUE / UNVERIFIED / FALSE."* ChatGPT's verdicts were then used directly to sort the findings:

- `FALSE` → "weakest, skip"
- `PARTIALLY TRUE` → "usable"
- `UNVERIFIED` → "weakest, skip"

The proposal was to "drill deeper on the strongest claims" — pursue only what GPT verified, skip the rest. Chapter 6's arguments were never read; no finding was mapped to a chapter argument before sorting. The only question asked was "did GPT verify it?"

## Impact

- 6 findings sorted by an irrelevant criterion (GPT confidence) instead of fit with the book's arguments
- Findings GPT marked `UNVERIFIED` or `FALSE` proposed for skipping — exactly the bucket where the book's most valuable evidence lives, since GPT's training data is mainstream scholarship and the book exists to challenge it
- User correction required to surface the failure pattern

## Root Cause

The research process has no structural mechanism to prevent ad-hoc verdict-soliciting prompts. Four CLAUDE.md rules prohibit this behavior in prose; all four are discipline-based. No script, guard, or required artifact enforces them at the point of decision.

The Evidence Filtering Commands describe a 5-step process for working with GPT output. All five steps were skipped and replaced with a single question: *"GPT, is this true?"* Nothing in the system prevented or detected this substitution.

Same class as PM-0001/PM-0002: the default for any evaluation task is to substitute mechanical scoring for human judgment. PM-0001 was keyword overlap scores. PM-0002 was the same operation under a renamed concept. PM-0004 is GPT confidence scores. The mechanism differs each time; the pattern is identical, and discipline-based prohibitions do not catch it.

## Action Items

- [x] [prevent] `build_coverage.py --research-prep` assembles the ChatGPT research prompt (mirrors `--embed-prep` for Step 2). The assembled prompt carries an anti-verdict header, the anti-pattern rules block, the chapter argument inventory, and a required output structure with no verdict field. The builder self-validates the assembled text and refuses to write if banned phrases (e.g. `TRUE / FALSE`, `rate confidence`) appear outside the negative-example block.
- [x] [prevent] `build_coverage.py --research-validate --batch-id NAME` validates a `research-eval.json` artifact mapping every batch finding to a `chapter_argument_id` resolvable in the chapter inventory, with a verdict drawn from the closed set `{embed, research, qa, skip_redundant, skip_tangential}` and a non-empty `what_finding_adds` and `verdict_justification`. The validator refuses to emit a presentable summary unless every finding has a real argument mapping; this is the only sanctioned path from GPT output to user-facing findings.
