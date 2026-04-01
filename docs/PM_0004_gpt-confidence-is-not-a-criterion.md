# PM-0004: GPT's Confidence Is Not a Criterion for the Book

## What Happened

Claude received 6 research findings about Greek mystery cult transmission to Church Fathers. Claude sent them to ChatGPT with the prompt: "For each claim, give me: VERDICT: TRUE / PARTIALLY TRUE / UNVERIFIED / FALSE." ChatGPT returned verdicts. Claude adopted those verdicts and used them to sort findings:

- GPT said FALSE → Claude said "weakest, skip"
- GPT said PARTIALLY TRUE → Claude said "usable"
- GPT said UNVERIFIED → Claude said "weakest, skip"

Claude proposed to "drill deeper on the strongest claims" — pursue only what GPT verified, skip the rest. Claude never read chapter 6's arguments. Claude never asked "does this finding strengthen an argument the book makes?" The only question Claude asked was "did GPT verify it?"

## Impact

- 6 research findings sorted by an irrelevant criterion — GPT's confidence instead of the book's arguments
- Findings GPT marked UNVERIFIED or FALSE were proposed for skipping — these may have been the most valuable leads
- 30+ messages of user correction before the root cause was identified
- Trust in Claude's ability to do independent research evaluation is damaged

## Why This Is Catastrophic

ChatGPT's confidence has zero bearing on whether a finding belongs in the book. Zero. Not a weak criterion, not a biased criterion — not a criterion at all. A fully verified irrelevant fact does not belong (the sun sets in the west). An unverified claim that strengthens a chapter's argument does belong — it goes to RESEARCH for sourcing.

If Claude filters by GPT's confidence, the book fills with whatever GPT happens to know — mainstream consensus, well-known trivia — regardless of whether it serves any argument. The book stops being a book about anything.

This book exists to present arguments that mainstream scholarship overlooks. GPT's training data IS mainstream scholarship. Using GPT's confidence as a filter systematically discards the book's most valuable evidence.

## How GPT Should Be Used

GPT is a powerful research tool. Assume 50% of what it says is true and 50% is false. You cannot tell which half is which without checking against primary sources. The true 50% is enormously valuable — it contains facts and connections that are extremely hard to find through any other research method. That is GPT's entire value.

GPT is also the biggest liar known to humanity and has been fired from every research project. Both things are true simultaneously.

**GPT's role:** discuss, enrich, help find sources, write drafts.
**Not GPT's role:** evaluate, judge, give verdicts, determine what goes in the book.

## Root Cause

The research process has no structural mechanism to prevent Claude from asking GPT for verdicts and adopting them. Four rules prohibit this behavior in prose, but all four are discipline-based — they rely on Claude reading and following them. No guard, no artifact, no automation enforces them.

The Evidence Filtering Commands (CLAUDE.md) describe a 5-step process for working with GPT output. Claude skipped all 5 steps and substituted a single question: "GPT, is this true?" Nothing in the system prevented or detected this substitution.

Same class as PM-0001: Claude's default for any evaluation task is automated scoring. PM-0001 was keyword extraction scores. PM-0004 is GPT confidence scores. Both substitute a mechanical shortcut for human judgment. The mechanism is different; the pattern is identical.

## Action Items

- [x] [detect] This PM documents the failure pattern. Same class as PM-0001 (automated scoring replacing human judgment).
- [ ] [prevent] The research query prompt to ChatGPT must be assembled by a script (like `build_coverage.py --embed-prep` assembles Step 2 context). The script injects anti-pattern rules and the correct query structure into the prompt, preventing Claude from composing ad-hoc prompts that ask for verdicts. (#104)
- [ ] [prevent] After receiving GPT output, Claude must produce a research evaluation artifact mapping each finding to a specific chapter argument before presenting to the user. Like pr-review.json forces review before push, a research-eval artifact forces evaluation before presentation. (#105)
