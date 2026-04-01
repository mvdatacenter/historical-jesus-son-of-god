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

Claude does not understand what research means in this project.

Claude thinks research = "determine if a claim is true." Research in this project = "find the primary source text so it can be read and evaluated by humans against the book's arguments." The output of research is a source — not a verdict.

Claude conflates three separate jobs:
1. **GPT's job:** discuss, enrich, find sources, write drafts
2. **Claude's job:** verify GPT's citations aren't hallucinated, evaluate findings against the book's arguments, catch bias
3. **The user's job:** decide what goes in the book

Claude did GPT's job (relay verdicts) instead of its own (evaluate against the book's arguments).

Four existing rules already prohibit this:
1. DD-0002: "No KEEP/SKIP decision may rest on ChatGPT's word alone."
2. CLAUDE.md: "ChatGPT's inability to find a source means nothing."
3. CLAUDE.md: "No finding may be rejected because ChatGPT cannot verify it."
4. DD-0002: "There is no 'weak' verdict."

All four were broken simultaneously. The rules existed. They were not followed.

## Action Items

- [x] [detect] This PM documents the failure pattern so it can be recognized in future sessions.
- [x] [prevent] Rules already exist (4 listed above). The problem was not missing rules — it was not following them.
- [x] [punish] If Claude presents findings filtered by GPT's confidence, the entire batch is discarded. Claude redoes from scratch: reread the full chapter, resend to GPT correctly, reevaluate against the book's arguments. The shortcut costs 3x the honest work.
