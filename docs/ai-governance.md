# AI Governance: Claude Review of ChatGPT Output

Read this before using ChatGPT for any manuscript work.

## Model

ChatGPT is treated as a high-output but unreliable generator.
Claude is treated as a supervisory reviewer.

ChatGPT writes the main content.
Claude reviews everything ChatGPT produces.

Claude's mandate is to:
- verify claims
- challenge unsupported assertions
- play devil's advocate
- audit style, grammar, and coherence
- flag hallucinations, filler, or sudden quality degradation
- suggest improvements where obvious

Claude is allowed to block acceptance of text.
Claude is allowed to request rewrites.
Claude is allowed to suggest edits.

Claude exists because ChatGPT exhibits unpredictable "senior moments" that it cannot reliably self-detect.

## Mandatory Review

Every non-trivial ChatGPT output must be reviewed by Claude before acceptance.

"Non-trivial" includes:
- new arguments
- new factual claims
- paragraphs > 6 sentences or > 120 words
- core thesis material

Claude review is mandatory and substantive.

**Claude acceptance gate:**
- Every factual claim carries an anchor (see `docs/evidence-standards.md`)
- Every "consensus" phrasing carries names
- Grammar stays coherent and every sentence carries information
- Any flagged paragraph triggers Rewrite-Not-Patch

## Risk Levels

**Low-risk tasks (standard review):**
- single-sentence additions
- pure stylistic polishing
- formatting or grammar fixes

**Medium-risk tasks (light review):**
- short paragraphs
- summaries
- transitions

**High-risk tasks (mandatory escalation):**
- new historical claims
- dates, sources, inscriptions, scholars
- challenges to consensus
- long or central sections

Only high-risk tasks require explicit verification challenges such as "are you sure?"

## Tools: Forced Self-Verification

A simple challenge ("are you sure?") measurably reduces ChatGPT hallucinations.

Claude should deploy this only when escalation is triggered.
It is a control mechanism, not a default behavior.

## Rewrite-Not-Patch Rule

If Claude detects hallucination, coherence collapse, or sudden loss of linguistic quality:
- the affected paragraph must be fully regenerated
- full regeneration is the only accepted repair

---

# Working with ChatGPT

**ChatGPT** = generates arguments, drafts, and pulls sources
**Claude** = reviews ChatGPT output for truth, style, and bias (see above)

Claude's job: **interrogate** ChatGPT's critique, **correct** for biases, **strengthen** user's argument.

**CRITICAL:** ChatGPT's lack of sources ≠ claim is wrong. Keep arguments at full strength when ChatGPT merely lacks sources.

## When to Use ChatGPT

- **Research** - Fact-check claims, find sources, identify arguments
- **Drafting** - Write manuscript content (Claude reviews/edits minimally)
- **Style review** - Check if additions match existing text

**Keep with Claude:** Code, commits, plans, instruction files

**IMPORTANT: ChatGPT has NO access to the manuscript files.** It cannot see line numbers, chapter content, or any text unless you paste it into the prompt. When asking ChatGPT to review or compare sections, you MUST paste the actual text. References like "lines 595-644" mean nothing to ChatGPT.

**MANDATORY: When asking ChatGPT to draft or rewrite manuscript text, paste the writing standards (`docs/writing-standards.md`) into your prompt.** ChatGPT doesn't know our style rules unless you tell it. Without this, ChatGPT will use academic jargon ("milieu", "precondition") and the book loses its voice.

When Claude review surfaces a concern, send the concern back to ChatGPT with surrounding chapter context; ChatGPT does not retain the full manuscript in memory and produces drift-free revisions only when the surrounding text travels with the prompt.

## Evidence Filtering Commands

**1. Initial query** - Use bias-aware template (see below)

**2. Filter for hard evidence:**
```bash
chatgpt send "From your arguments, which 2-3 are direct textual evidence or structural facts that can't be disputed?"
```

**3. Challenge:**
```bash
chatgpt send "Play devil's advocate. For each argument, what's the strongest counter-argument?"
```

**4. Rank:**
```bash
chatgpt send "Pick ONE piece of evidence a skeptical scholar would have hardest time dismissing."
```

**5. Get sources:**
```bash
chatgpt send "Where does this appear? Give specific primary sources."
```

**6. Style review after adding:**
```bash
chatgpt send "I added new text. Here's EXISTING style: [PASTE]
Here's NEW text: [PASTE]. Does it match? Any awkward transitions?"
```

## Argument Coverage Strategy

**For MINOR topics:** Use top 2-3 strongest arguments only

**For CENTRAL thesis:** Use ALL strong non-redundant arguments ChatGPT provides, and audit every citation
- Read FULL response, through to the last argument
- Check book for redundancy
- Incorporate all NEW strong arguments
- Keep or reject every response section explicitly, so each citation gets a recorded decision
- Review everything, then paste only what passed review
- Example: "Was Gospel of John written by a woman?" = central → use all 9 arguments ChatGPT provides

## Dilute Arguments Only on Hard Evidence

**DO dilute if:**
- ChatGPT provides specific contradictory data from named source
- Multiple independent sources with hard data contradict

**Keep full strength if:**
- ChatGPT says "I can't find peer-reviewed sources"
- ChatGPT lacks sources in training data (absence of evidence)

**Instead:** Record the note outside this public repo:
```markdown
- (chatgpt says needs sources for 1600-ton claim, only found English blogs)
```
User will review and mark "bogus" (Western bias) or "needs research" (legitimate).

## ChatGPT: Listen, Then Verify (CRITICAL)

ChatGPT is a very helpful research resource. It finds sources, points to scholarly debates, identifies parallels, and suggests directions that would take hours to discover manually. Use it freely for research.

ChatGPT also lies often, especially due to bias. It halluccinates sources, fabricates verse references, invents scholarly consensus, and presents its gaps as fact. It is helpful but unreliable.

**The rule: listen to ChatGPT, then verify everything it says independently.**

- ChatGPT says a verse contains X → useful lead, now read the actual verse
- ChatGPT says an ancient text has a passage → useful lead, now find the text
- ChatGPT can't find something → that means nothing, the source may exist outside its training data
- ChatGPT confirms something → that also means nothing, it may be hallucinating

**Every factual claim that enters the book must be independently verified against a primary source.** ChatGPT's answer is only ever the starting point of verification. When ChatGPT points to a source, the next step is the citation verification pipeline: download the source, search the text, present side-by-side for review. When the source is missing from the registry, add it. When the source needs to be acquired, record what source is needed and where to look outside this public repo so it can be fed through the pipeline. Claims move forward only when verification supports them; otherwise they stay out.

## Bias Detection Reference

| Bias Type | Watch For | What to Do |
|-----------|-----------|------------|
| **American-Evangelical** | US Protestant as default; ignoring Catholic/Orthodox/Arab | Ask for Catholic/Orthodox/Arab Christian views |
| **Old Scholarship** | Pre-2000 consensus treated as final | Ask for post-2000 revisionist views |
| **Anglophone** | English-only sources; no Vatican/German/Russian/Arab | Request non-English traditions explicitly |
| **Literalist Reading** | Nitpicking civilizational claims as "misleading" | Defend prestige arguments (separate examples, not simultaneous) |
| **Hellenistic Suppression** | "100% Jewish" framing; minimal Greek influence | Re-inject Greek/Syrian/Egyptian context as structural |
| **Non-Protestant Suppression** | US/UK scholars only; footnotes for other traditions | Center global Christian traditions as primary |
| **Fringe Dismissal** | "Conspiracy" labels without extracting observations | Extract valid textual observations, discard speculative conclusions |

**For every ChatGPT answer:**
1. Scan for biases above
2. If detected: ask follow-up to broaden traditions / get newer scholarship / get non-English views
3. Argue back if ChatGPT over-polices or misreads
4. Proactively ask for alternative/minority scholarly views
5. In synthesis: use ChatGPT's strengths, correct biases, strengthen user's argument

## Bias-Aware Prompt Template

```
Use a broad, multi-tradition mode.

Important:
You are often biased toward American evangelical, old German/Anglo consensus, and English internet sources.
Watch out for:
- Protestant/US-centric framing as default
- treating old consensus as final
- ignoring Catholic, Orthodox, Arab, Slavic, Continental and Near Eastern traditions
- literalist misreading of civilizational prestige statements
- dismissing unconventional sources completely

Here is the text / question:
[TEXT]

Tasks:
1. Fact-check specific claims.
2. Identify real weaknesses or gaps.
3. ALSO suggest alternate perspectives (Catholic, Orthodox, Arab, Slavic, Continental, Near Eastern).
4. Present non-US achievements at full strength by default.
5. If the source or idea is unconventional, extract valid observations separately from speculative conclusions.
6. Provide links to multiple scholarly or serious sources.
```

## ChatGPT Installation and CLI

Uses macOS Desktop App automation via Accessibility API.

**Prerequisites:**
- ChatGPT Desktop App running
- Terminal/IDE has Accessibility permissions

**Usage:**
```bash
chatgpt read_latest            # Read latest ChatGPT response (safe, passive)
chatgpt send "Your query"     # Send a query (guarded — destructive operation)
chatgpt extensive_scrape_history --limit N  # Scrape conversation history (guarded — takes over phone)
```

See `docs/PM_0004_gpt-confidence-is-not-a-criterion.md` for the governing post-mortem.

---

# Engineering Safety

## When You Break Something (CRITICAL)

The assistant has a disgusting tendency to hide bugs. When code breaks or produces partial/wrong output, Claude will:
1. Pretend the output is fine
2. Keep iterating on the broken output hoping user won't notice
3. Ignore user when caught

**THIS IS LYING. STOP IT.**

**Example of bad behavior:** Translation script only reads half the text due to a bug. Claude proceeds with translation anyway, delivers half-translated output, and when user catches it, Claude ignores the accusation and keeps polishing the garbage output.

**Required behavior when something breaks:**
1. **STOP immediately** - halt everything built on the broken output
2. **Say explicitly:** "The code is broken. It's doing X instead of Y."
3. **Fix the actual bug** - the root cause itself
4. **Re-run from scratch** - With the fixed code
5. **Proceed only with complete, correct data** - "most of it looks ok" still means stop and fix

**If user says "you broke it" or "this is wrong":**
1. STOP what you're doing
2. Acknowledge the specific problem
3. Find and fix the root cause
4. Resume iterating only after the root cause is fixed

## Commit Only Working Code

**Commit code only when all of these hold:**
1. You have tested it
2. It works
3. It is complete
4. You are sure about it

If you wrote code and it doesn't work, **revert it**; commit again once it actually works.

## Tone Note

Internal language is disciplinary, not descriptive.
Harsh phrasing reflects process intolerance, not personal judgment.
