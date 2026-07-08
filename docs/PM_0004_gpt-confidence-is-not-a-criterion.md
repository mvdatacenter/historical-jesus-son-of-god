# PM-0004: GPT Verdicts Adopted as Research Filter

## What Happened

Six research findings about Greek mystery cult transmission to Church Fathers were sent to ChatGPT with the prompt: *"For each claim, give me: VERDICT: TRUE / PARTIALLY TRUE / UNVERIFIED / FALSE."* ChatGPT's verdicts were then used directly to sort the findings:

- `FALSE` → "weakest, skip"
- `PARTIALLY TRUE` → "usable"
- `UNVERIFIED` → "weakest, skip"

The proposal was to "drill deeper on the strongest claims" — pursue only what GPT verified, skip the rest. Chapter 6's arguments were never read; no finding was mapped to a chapter argument before sorting. The only question asked was "did GPT verify it?"
This sorted 6 findings by GPT confidence instead of fit with the book's arguments, and findings marked `UNVERIFIED` or `FALSE` were proposed for skipping even though that bucket can contain the book's most valuable evidence.

## Root Cause

The research process has no structural mechanism to prevent ad-hoc verdict-soliciting prompts. Four CLAUDE.md rules prohibit this behavior in prose; all four are discipline-based. No script, guard, or required artifact enforces them at the point of decision.

The Evidence Filtering Commands describe a 5-step process for working with GPT output. All five steps were skipped and replaced with a single question: *"GPT, is this true?"* Nothing in the system prevented or detected this substitution.

Same class as PM-0001/PM-0002: the default for any evaluation task is to substitute mechanical scoring for human judgment. PM-0001 was keyword overlap scores. PM-0002 was the same operation under a renamed concept. PM-0004 is GPT confidence scores. The mechanism differs each time; the pattern is identical, and discipline-based prohibitions do not catch it.

## Action Items

- [x] [prevent] The private research repo's `build_coverage.py --research-prep` assembles the ChatGPT research prompt with an anti-verdict header, the anti-pattern rules block, the chapter argument inventory, and a required output structure with no verdict field; implemented in mvdatacenter/historical-jesus-son-of-god-research#6.
- [x] [prevent] The private research repo's `build_coverage.py --research-validate --batch-id NAME` validates every batch finding against a real `chapter_argument_id`, closed-set verdict, non-empty `what_finding_adds`, and `verdict_justification`; implemented in mvdatacenter/historical-jesus-son-of-god-research#6.
