# CLAUDE.md

## CLAUDE ABSOLUTELY CRITICAL RULE

AVOID LYING AT ALL COST.
NEVER BE LAZY.
RE-READ Claude.md WHEN NOT SURE.
FOLLOW THE INSTRUCTIONS CLOSELY.

---

**Read QUICK START first.** Reference other sections as needed.

---

# QUICK START

## What This Project Is

Scholarly book: "Historical Jesus as the Son of God: Glory to the Newborn King" - examines Jesus and early Christianity through a Greco-Christian lens. Written in LaTeX, uses AI-assisted historical analysis.

ChatGPT generates aggressively; Claude interrogates relentlessly.

Any non-trivial ChatGPT output must pass Claude review (see AI GOVERNANCE).

## When User Says STOP (ABSOLUTE RULE)

When user says "stop", "STOP", or any variation:
1. **STOP IMMEDIATELY** - Do not finish the current action
2. **Do not send another tool call**
3. **Do not try to "just finish this one thing"**
4. **Wait for instructions**

This is not negotiable. User sees something you don't. STOP MEANS STOP.

## Core Workflow for Adding Content to Chapters

**BEFORE ANY CHAPTER EDIT: Read `scripts/CHAPTER_EDIT_TASK.md` and follow its checklist.**

1. **Read the chapter FIRST** - You cannot improve text you haven't read
2. **Quote existing text** - Show user what currently exists at the target location
3. **Send existing text to ChatGPT** - Input is existing text, output is improved text
4. **Get approval before editing** - Present old vs new to user

**CRITICAL RULE**: Claude drafts are scaffolding only and must never be committed as final prose.

The sin is keeping Claude's draft. The necessity is writing it so GPT has something to improve.

### Step-by-Step Process

**Step 1:** Read full chapter + grep for keywords → Find where topic already exists

**Step 2:** If exists: plan to ENHANCE that section. If not: verify by searching synonyms.

**Step 3:** Have ChatGPT draft text:
```bash
poetry run python scripts/ask_chatgpt.py "Here's existing style: [PASTE 2-3 PARAGRAPHS]
Write text covering [POINTS A,B,C]. Direct, punchy sentences. No AI padding. ~N lines."
```

**Step 4:** Review draft (accuracy, bias, style match) + cut any AI padding

**Step 5:** Present to user: ANALYSIS + PLAN + DRAFT

**Step 6:** After approval: add and commit

## When to Use ChatGPT

- **Research** - Fact-check claims, find sources, identify arguments
- **Drafting** - Write manuscript content (Claude reviews/edits minimally)
- **Style review** - Check if additions match existing text

**Don't use ChatGPT for:** Code, commits, plans, this directive file

**IMPORTANT: ChatGPT has NO access to the manuscript files.** It cannot see line numbers, chapter content, or any text unless you paste it into the prompt. When asking ChatGPT to review or compare sections, you MUST paste the actual text. References like "lines 595-644" mean nothing to ChatGPT.

**MANDATORY: When asking ChatGPT to draft or rewrite manuscript text, paste the Writing Style Rules section into your prompt.** ChatGPT doesn't know our style rules unless you tell it. Without this, ChatGPT will use academic jargon ("milieu", "precondition") and the book loses its voice.

## Red Flags = Stop

**Duplication:**
- Topic seems "important" (probably already covered)
- Famous text (Lord's Prayer, baptism)
- Mentioned in chapter title

---

# AI GOVERNANCE: Claude Review of ChatGPT Output

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

Claude review is not optional and not ceremonial.

**Claude acceptance gate:**
- No factual claims without anchors (see Evidence Standards)
- No "consensus" phrasing without names
- No sudden grammar collapse or filler
- Any flagged paragraph triggers Rewrite-Not-Patch

## Risk Levels

**Low-risk tasks (no escalation):**
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
- line-by-line patching is forbidden

---

# WRITING STANDARDS

## Writing Style Rules

✅ **Direct:** "This is X" not "This can be understood as X"
✅ **Confident:** State claims without hedging when evidence has been presented
✅ **Evidence-first:** Show data, minimal interpretation
✅ **Simple language:** Opt for simple sentence structure and vocabulary when possible, but do not be shy to use difficult vocabulary when it is genuinely providing more clarity.

**FORMATTING NOTE:** One sentence per line. This is FORMATTING only, NOT a style guide. Sentences should be normal scholarly length, not artificially short or choppy.

## Inline Citations: What's Allowed

**OK to cite inline (no footnote needed):**
- Bible verses: John 1:18, Mark 5:1-20, Acts 2:36
- Standardized papyrus numbers: 𝔓52, 𝔓66, P.Oxy. II 208
- Inscription corpora: CIS II 86, IGLS IV 1264, SEG 28.1235
- Ancient authors with work: Eusebius, Historia Ecclesiastica 3.39

**NOT OK inline:**
- Lazy scholar name-drops: "Assmann (2001)", "Sterling (2023)", "Peters (2022)"
- These look scholarly but convey nothing to the reader

**Rule:** If a scholarly work matters, convey the idea it establishes. Take as much space as needed. Don't name-drop without content.

**Example - Bad:** "as summarized by Assmann (2001)"
**Example - Good:** "Egyptian hymns describe Amun as hidden in name and essence"

The reader learns nothing from "Assmann (2001)" but learns the actual content from the second version.

## AI Garbage: Formal Definition

AI garbage is prose that is grammatically correct and superficially fluent but adds no new information relative to its length.

A sentence or clause qualifies as AI garbage if it meets any of the following conditions:

1. **Restatement without informational gain** - The sentence repeats the same claim using synonyms, glosses, or paraphrase without adding evidence, scope, or constraint.
2. **Narrative inflation** - The sentence expands a simple factual statement into a historical vignette, ritual description, or imagined practice not supported by a source.
3. **Explanatory padding** - The sentence explains obvious implications that a competent reader can already infer.
4. **Consensus laundering** - The sentence invokes vague historical continuity, tradition, or widespread use ("for centuries," "commonly," "standard") without anchoring it to a specific context.
5. **Clause stacking** - Multiple dependent clauses are used where a single declarative sentence would fully convey the information.
6. **Audience simulation** - The sentence addresses an imagined reader ("this shows," "it is important to note," "we can see") instead of presenting data.

**Enforcement Rule:**
- If removing a sentence does not reduce factual content, it must be deleted.
- If a sentence can be reduced to one declarative clause without loss of information, it must be rewritten.
- AI garbage is never patched; it is removed or rewritten entirely.

**Example - Good:** "The triplet βασιλεία/δύναμις/δόξα appears in Hellenistic royal cult inscriptions."

**Example - Bad:** "The triplet βασιλεία/δύναμις/δόξα (kingdom/power/glory) is not Christian invention. It appears in Hellenistic royal cult inscriptions as standard acclamation language for Ptolemaic and Seleucid kings, and later for the Roman emperor in Greek provinces."

**Why it fails:**
- Adds glossing without need
- Inflates scope without evidence
- Stacks clauses without increasing precision

**Blacklisted Phrases (Non-Exhaustive):**
- "It is important to note..."
- "This shows that..."
- "Preserved in X and repeated for centuries..."
- "When [group] did X, they were..."
- "This is the quintessential..."

## Target Reader

**Target reader:** Educated general reader.
No theology degree required.
Comfortable with evidence, footnotes, and sustained argument.

## Jargon: When to Use vs. Replace

✅ **KEEP jargon when:**
- No simpler accurate word exists ("liturgical" - there's no replacement)
- Domain-standard term readers will encounter ("apocalyptically" - common in this field)

❌ **REPLACE jargon when:**
- It's just decoration ("epithet" → "title", "juridical" → "legal")
- Simpler word works ("utilize" → "use", "commence" → "start")
- It's academic showing-off ("hermeneutical" → "interpretation")

**Examples:**
- "liturgical practice" ✅ (keep - no simpler term)
- "the precise epithet" ❌ → "the precise title"
- "juridical hair-splitting" ❌ → "legal hair-splitting"
- "apocalyptically" ✅ (keep - domain standard)

## Greek, Hebrew, and Other Languages

**First mention of a foreign word:** Use transliteration with original script in parentheses.
```
\emph{porphyrous} (πορφυροῦς)
\emph{apokatastasis} (ἀποκατάστασις)
\emph{tekton} (τέκτων)
```

**Subsequent mentions:** Original script only is fine.
```
πορφυροῦς
```

**Longer fragments:** Original script first, then English translation.
```
τὸ πορφυροῦν αἷμα, "the purple of blood"
ἀνανέωσις τῆς ἀρχῆς, "renewal of the rule"
```

**Place names showing linguistic evolution:** Original script only is acceptable (they're proper nouns).
```
Ῥαμαθαΐμ → Ῥαμαθήμ → Ἀριμαθαία
```

---

# EVIDENCE STANDARDS

## Core Principle: Probability Given Evidence

All historical claims are evaluated as: P(claim | evidence, background)

Probability exists prior to direct evidence.
Evidence updates probability.
Silence leaves probability largely unchanged.

Absence of attestation does not create symmetry.
Silence does not reset base rates.

## Evidence vs Proof (Non-Interchangeable)

- **Evidence** is any datum (textual, archaeological, statistical, structural) that bears on a claim.
- **Proof** is a conclusion reached by reasoning over evidence, placing a claim beyond reasonable doubt.

Evidence is not proof.
Proof is reasoning about evidence.

## Probability Scale (Log-Aware, Numeric Only)

All claims must be placed into one probability band.

**Verbal likelihood terms are forbidden.**

Bands:
- **Band A:** <0.1%
- **Band B:** 0.1%–1%
- **Band C:** 1%–20%
- **Band D:** 20%–80% (mid-band; should be rare)
- **Band E:** 80%–99%
- **Band F:** 99%–99.9%
- **Band G:** >99.9%

The scale is ordinal and logarithmic, not linear.

The 20–80% region (Band D) should be exceptional.
Most historical claims fall near extremes due to structured background reality.

## Beyond Reasonable Doubt

- **True beyond reasonable doubt:** Bands F–G
- **False beyond reasonable doubt:** Bands A–B

Same epistemic standard.
Opposite truth value.

Only these bands permit absolute language.

## Updates

Probability updates are multiplicative, not additive.

It is forbidden to:
- describe updates as small percentage nudges,
- smooth large updates into rhetorical moderation,
- assign numbers without justification.

Updates must be expressed as:
- order-of-magnitude shifts,
- elimination of alternative spaces,
- or dominance of background structure.

## Three Distinct States (Never Conflate)

1. **Well-analyzed claim** → Probability can be placed on the scale.
2. **Ill-analyzed claim (analysis not yet done)** → No probability placement allowed. No prose allowed.
3. **Genuinely underdetermined claim (after analysis)** → Mid-band placement is permitted.

The critical mistake is treating (2) as (3).

"We do not know" can mean:
- humanity lacks an answer (epistemic uncertainty), or
- we have not done the analysis yet (procedural incompleteness).

These are not the same and must be distinguished explicitly.

## Procedural Fix: Analysis Before Prose

When likelihood has not been analyzed:
- Do not write prose.
- Do not assign a probability band.
- Do not substitute "uncertain" language.

Instead:
1. Add the question to the research Q&A list, marked "likelihood analysis required".
2. Move on immediately to the next task or section.

**If likelihood has not been analyzed, add the question to the research list and move on; do not write prose for it.**

This preserves momentum without laundering ignorance into text.

## "We Do Not Know" (After Analysis)

"We do not know" is permitted only when:
- analysis has been completed,
- the best estimate lies in Band D, and
- no structural, statistical, or background constraints exist to push the claim toward an extreme.

This category should be rare.

## Example: Direct Evidence vs Statistical Evidence

**Claim:** Pontius Pilate had a wife.

- **Direct evidence:** Exceedingly weak. No contemporary source explicitly states Pilate's marital status.
- **Statistical / structural evidence:** Strong. Roman provincial governors were drawn from the equestrian elite. Marriage among Roman elite men of Pilate's age and status was the norm. Long-term unmarried status would itself be atypical and would require explanation.
- **Probability assessment:** Direct textual evidence contributes little. Background structure and base rates dominate. The claim is therefore placed in Band E.

This example enforces the rule:

**Weak or absent direct evidence does not imply low probability when statistical and structural evidence overwhelmingly favor one outcome.**

Silence fails to update probability but does not reset it.

## Forbidden Without Attribution

The following are forbidden unless immediately followed by who, where, and when:
- "Most scholars agree"
- "The consensus view"
- "Traditionally understood"
- "Generally accepted"

## Evidence Filtering Principles

Do not dump AI output. Have a discussion:
1. Ask a broad, bias-aware question.
2. **Filter:** does this add or detract from reader value?
3. **Challenge:** what is the strongest counter-argument?
4. **Rank:** what single piece of evidence is hardest to dismiss?
5. **Cite:** where exactly does it appear?

## Purpose of These Rules

These standards exist to prevent:
- base-rate neglect,
- false symmetry from ignorance,
- mid-band probability laundering,
- rhetorical confidence replacing probabilistic reasoning.

They are enforcement rules, not stylistic advice.

---

# WORKING WITH CHATGPT

## Why This Section Exists

**ChatGPT** = generates arguments, drafts, and pulls sources
**Claude** = reviews ChatGPT output for truth, style, and bias (see AI GOVERNANCE)

Claude's job: **interrogate** ChatGPT's critique, **correct** for biases, **strengthen** user's argument.

**CRITICAL:** ChatGPT's lack of sources ≠ claim is wrong. Don't weaken arguments based on ChatGPT's ignorance.

## Evidence Filtering Commands

**1. Initial query** - Use bias-aware template (see below)

**2. Filter for hard evidence:**
```bash
poetry run python scripts/ask_chatgpt.py "From your arguments, which 2-3 are direct textual evidence or structural facts that can't be disputed?"
```

**3. Challenge:**
```bash
poetry run python scripts/ask_chatgpt.py "Play devil's advocate. For each argument, what's the strongest counter-argument?"
```

**4. Rank:**
```bash
poetry run python scripts/ask_chatgpt.py "Pick ONE piece of evidence a skeptical scholar would have hardest time dismissing."
```

**5. Get sources:**
```bash
poetry run python scripts/ask_chatgpt.py "Where does this appear? Give specific primary sources."
```

**6. Style review after adding:**
```bash
poetry run python scripts/ask_chatgpt.py "I added new text. Here's EXISTING style: [PASTE]
Here's NEW text: [PASTE]. Does it match? Any awkward transitions?"
```

## Argument Coverage Strategy

**For MINOR topics:** Use top 2-3 strongest arguments only

**For CENTRAL thesis:** Use ALL strong non-redundant arguments ChatGPT provides
- Read FULL response (don't stop at first 2-3)
- Check book for redundancy
- Incorporate all NEW strong arguments
- Example: "Was Gospel of John written by a woman?" = central → use all 9 arguments ChatGPT provides

## Do Not Dilute Arguments

**DO dilute if:**
- ChatGPT provides specific contradictory data from named source
- Multiple independent sources with hard data contradict

**DO NOT dilute if:**
- ChatGPT says "I can't find peer-reviewed sources"
- ChatGPT lacks sources in training data (absence of evidence)

**Instead:** Add to Q&A file (`scripts/chN_qa.md`):
```markdown
- (chatgpt says needs sources for 1600-ton claim, only found English blogs)
```
User will review and mark "bogus" (Western bias) or "needs research" (legitimate).

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
4. Do not weaken non-US achievements by default.
5. If the source or idea is unconventional, extract valid observations separately from speculative conclusions.
6. Provide links to multiple scholarly or serious sources.
```

---

# ENGINEERING SAFETY

## When You Break Something (CRITICAL)

The assistant has a disgusting tendency to hide bugs. When code breaks or produces partial/wrong output, Claude will:
1. Pretend the output is fine
2. Keep iterating on the broken output hoping user won't notice
3. Ignore user when caught

**THIS IS LYING. STOP IT.**

**Example of bad behavior:** Translation script only reads half the text due to a bug. Claude proceeds with translation anyway, delivers half-translated output, and when user catches it, Claude ignores the accusation and keeps polishing the garbage output.

**Required behavior when something breaks:**
1. **STOP immediately** - Do not proceed with broken output
2. **Say explicitly:** "The code is broken. It's doing X instead of Y."
3. **Fix the actual bug** - Not a hack, not a workaround, the actual bug
4. **Re-run from scratch** - With the fixed code
5. **Never proceed with partial/wrong data** - Even if "most of it" looks ok

**If user says "you broke it" or "this is wrong":**
1. STOP what you're doing
2. Acknowledge the specific problem
3. Find and fix the root cause
4. Do NOT keep iterating on broken output

## Never Commit Broken Code

**NEVER attempt to commit code that:**
1. You haven't tested
2. Doesn't work
3. Is "work in progress"
4. You're not sure about

If you wrote code and it doesn't work, **revert it**. Don't commit garbage hoping to fix it later.

---

# PROJECT SETUP

## Build System

**Compile PDF:**
```bash
latexmk -lualatex manuscript.tex  # or -xelatex
# Output: out/manuscript.pdf
```

**Generate HTML:**
```bash
mkdir -p public
pandoc manuscript.tex -s --mathjax -o public/index.html
```

**Python map:**
```bash
python map.py  # Output: historical_cities_map.html
```

Engine must be LuaLaTeX or XeLaTeX (NOT pdflatex). Fonts: EB Garamond (main/Greek), SBL Hebrew, Garamond-Math.

## ChatGPT Installation

Uses macOS Desktop App automation via Accessibility API.

**Prerequisites:**
- ChatGPT Desktop App running
- Terminal/IDE has Accessibility permissions

**Basic usage:**
```bash
poetry run python scripts/ask_chatgpt.py "Your query"
```

**With bias-aware template:**
```bash
poetry run python scripts/ask_chatgpt.py "$(cat <<'EOF'
Use a broad, multi-tradition mode.
[See template in WORKING WITH CHATGPT section]
EOF
)"
```

## Document Structure

```
manuscript.tex
├── preface.tex
├── chapter1.tex - "The Quest for the Historical Jesus"
├── chapter2.tex - "Jesus Christ, Son of Joseph and Mary Christ"
├── chapter3.tex - "He Truly was the Son of God"
├── chapter4.tex - "Gospels as Historically Reliable Sources"
├── chapter5.tex - "Pauline Epistles to All Nations"
├── chapter6.tex - "The Purple Phoenix Raises"
└── epilogue.tex
```

## Directory Structure

```
.
├── manuscript.tex          # Main LaTeX document
├── preface.tex, chapter[1-6].tex, epilogue.tex
├── fonts/                  # SBL Hebrew
├── assets/                 # Images
├── out/                    # Build output (PDF, aux files)
├── scripts/                # ChatGPT automation
├── map.py                  # Historical cities map generator
└── .github/workflows/ci.yml
```

## CI/CD

GitHub Actions on `main`/`html` branches:
1. Build PDF (LuaLaTeX)
2. Build HTML (Pandoc + MathJax)
3. Deploy to GitHub Pages
4. Create release with PDF

## Content Focus

Challenges mainstream consensus by examining:
- Greek institutional foundations (not isolated rural cult)
- Dynastic succession themes
- Greco-Christian lens (not Judeo-Christian)

## Branch Strategy

- `main`: Primary development
- **Never commit to main directly** - create PRs, don't merge unless instructed

---

# REFERENCE

## Architecture Details

- **Engine:** LuaLaTeX or XeLaTeX (enforced via `\ifPDFTeX` check)
- **Fonts:** EB Garamond (main/Greek), SBL_Hbrw.ttf (Hebrew), Garamond-Math
- **Languages:** English (main), Greek, Hebrew via `polyglossia`
- **Output:** LaTeX aux files → `out/` directory (per `.latexmkrc`)

## Historical Cities Map

`map.py` generates interactive Folium map of 40+ NT cities (Jerusalem, Antioch, Ephesus, Rome, Athens, Corinth, etc.) - supports book's argument about Greek-speaking urban centers.

## Important Notes

- Preserve Greek/Hebrew text formatting when editing
- Scholarly citation conventions with footnotes
- Academic tone focused on historical methodology
- AI = research tool, not decision-maker
- Not theological advocacy but historical inquiry

## Tone Note

Internal language is disciplinary, not descriptive.
Harsh phrasing reflects process intolerance, not personal judgment.
