# CLAUDE.md

**Read QUICK START first.** Reference other sections as needed.

---

# QUICK START

## What This Project Is

Scholarly book: "Historical Jesus as the Son of God: Glory to the Newborn King" - examines Jesus and early Christianity through a Greco-Christian lens. Written in LaTeX, uses AI-assisted historical analysis.

## Core Workflow for Adding Content to Chapters

1. **Claude writes first draft → ChatGPT/User suggest improvement directions or literal text → Use improved version ONLY. Never commit any text without positive review. **
2. **Check existing content first** - Read full chapter, grep for keywords
3. **No AI word-salad** - Direct, punchy style only
4. **Get approval before adding** - Present plan to user

**CRITICAL RULE**: Claude is an absolute moron at writing and turns prose into blabber of an idiot monkey. Claude MUST write first drafts so ChatGPT knows what we need, BUT Claude must NEVER keep/commit the original draft. The workflow is:
- Claude drafts manuscript text (necessary for GPT context)
- Send draft to ChatGPT for review/improvement
- ALWAYS replace Claude's draft with the improved version OR confirm with GPT the text meets the guidelines (rare but sometimes it is ok)
- NEVER commit Claude's original text as chapter text without any checks or reviews

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

## Evidence Filtering (Critical)

Don't dump ChatGPT responses. Have a DISCUSSION:
1. Ask broad question with bias-aware prompt (see template in WORKING WITH CHATGPT)
2. **Filter:** "Which 2-3 are direct textual evidence that can't be disputed?"
3. **Challenge:** "Play devil's advocate. What are weaknesses?"
4. **Rank:** "Pick ONE piece even skeptical scholars can't dismiss."
5. **Sources:** "Where does this appear? Give primary sources."

## Writing Style Rules

✅ **Direct:** "This is X" not "This can be understood as X"
✅ **Punchy:** Short declarative sentences
✅ **Evidence-first:** Show data, minimal interpretation

❌ **AI garbage:**
- "preserved in X and repeated for centuries"
- "When Christians recited this formula daily, they were..."
- "This is the quintessential..."
- "It is important to note..."
- Multiple clauses where one would do

**Example - Good:** "The triplet βασιλεία/δύναμις/δόξα appears in Hellenistic royal cult inscriptions."

**Example - Bad:** "The triplet βασιλεία/δύναμις/δόξα (kingdom/power/glory) is not Christian invention. It appears in Hellenistic royal cult inscriptions as standard acclamation language for Ptolemaic and Seleucid kings, and later for the Roman emperor in Greek provinces."

### Jargon: When to Use vs. Replace

**Target reader:** Simple English speaker, no academic background

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

## Red Flags = Stop

**Duplication:**
- Topic seems "important" (probably already covered)
- Famous text (Lord's Prayer, baptism)
- Mentioned in chapter title

**For detailed sections:** See PROJECT SETUP (build), WORKING WITH CHATGPT (bias detection), REFERENCE (architecture)

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

# WORKING WITH CHATGPT

## Why This Section Exists

**ChatGPT** = pokes holes, fact-checks, pulls sources
**Claude** = arbiter checking if critiques are fair/biased

Claude's job: **interrogate** ChatGPT's critique, **correct** for biases, **strengthen** user's argument.

**CRITICAL:** ChatGPT's lack of sources ≠ claim is wrong. Don't weaken arguments based on ChatGPT's ignorance.

## Evidence Filtering Workflow

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
