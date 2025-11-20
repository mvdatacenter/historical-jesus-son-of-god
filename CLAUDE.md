# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a scholarly book project titled "Historical Jesus as the Son of God: Glory to the Newborn King" that uses AI-assisted historical analysis to examine Jesus and early Christianity through a Greco-Christian rather than Judeo-Christian lens. The project is written in LaTeX and compiled to both PDF and HTML outputs.

## Build System

### Compiling the Book

The project uses **LuaLaTeX** or **XeLaTeX** (NOT pdflatex) due to custom font requirements:

```bash
# Compile the full manuscript to PDF
latexmk -lualatex manuscript.tex

# Or using xelatex
latexmk -xelatex manuscript.tex

# Output will be in: out/manuscript.pdf
```

The build configuration is in `.latexmkrc` and specifies that `xelatex` or `lualatex` should be used for all PDF compilation.

### Generating HTML

```bash
# Convert to HTML using pandoc
mkdir -p public
pandoc manuscript.tex -s --mathjax -o public/index.html
```

### Python Map Utility

```bash
# Generate interactive map of historical cities
python map.py

# Output: historical_cities_map.html
```

This uses Python 3.12.2+ with the `folium` library for geographical visualization.

### ChatGPT Integration

This project uses ChatGPT (via web browser automation with Playwright) for fact-checking and bias-corrected research.

**Prerequisites:**
- Playwright installed via Poetry (already in dependencies)
- Chromium browser installed: `poetry run playwright install chromium`
- **ONE-TIME SETUP**: Login to ChatGPT web:
  ```bash
  poetry run python scripts/chatgpt_web.py init
  ```
  This opens a browser window. Log in to ChatGPT, then close the window. Your session is saved in `chatgpt_profile/` directory.

**How Claude Should Use It:**

```bash
# Basic usage - ask a question and get response
poetry run python scripts/ask_chatgpt.py "Your query here"

# Via Bash tool in Claude Code with MASTER DIRECTIVE template
poetry run python scripts/ask_chatgpt.py "$(cat <<'EOF'
Use a broad, multi-tradition mode.

Important:
You are often biased toward American evangelical, old German/Anglo consensus...
[use template from MASTER DIRECTIVE section 9]

Here is the text / question:
[your actual question]
EOF
)"
```

**Low-level commands (for debugging):**

```bash
# Send a prompt and wait for response
poetry run python scripts/chatgpt_web.py send "Your question"

# Read last response without sending
poetry run python scripts/chatgpt_web.py read

# Send without waiting for response
poetry run python scripts/chatgpt_web.py send --no-wait "Your question"
```

**Important:** Always use the reusable prompt skeleton from the MASTER DIRECTIVE (section 9) to counter ChatGPT's biases when querying.

### How to Use ChatGPT Properly: Filter for Strongest Evidence

**DO NOT just dump questions and copy ChatGPT's response.** Instead, have a DISCUSSION to identify hard evidence:

1. **Initial query** - Ask the broad question using MASTER DIRECTIVE template
2. **Filter for strongest evidence** - Follow up: "From your arguments, which 2-3 are direct textual evidence (specific Greek words, verses) or structural facts that can't be disputed? Don't give me interpretive arguments like 'suggests' - give me rock-solid evidence."
3. **Play devil's advocate** - Challenge each piece: "Play devil's advocate against your own arguments. For each one, what's the strongest counter-argument? What are the weaknesses?"
4. **Rank by undeniability** - Ask: "If you could only pick ONE piece of evidence that even a skeptical mainstream scholar would have hardest time dismissing, which would it be?"
5. **Get sources** - If the evidence is strong: "Where does this appear? Give me specific primary sources (texts, inscriptions, archaeological sites)."
6. **Review additions for style** - After writing new text based on the evidence, ask ChatGPT to review it: "I added new text to the book. Does it match the existing writing style? Is the tone consistent? Any awkward transitions or sentences that need fixing?" Include samples of existing text for style reference.

**Example workflow:**
```bash
# Step 1: Initial question with MASTER DIRECTIVE
poetry run python scripts/ask_chatgpt.py "$(cat <<'EOF'
Use a broad, multi-tradition mode.
[MASTER DIRECTIVE template]
Question: Why is non-coronation interpretation of baptism problematic?
EOF
)"

# Step 2: Filter for hard evidence
poetry run python scripts/ask_chatgpt.py "From your arguments, which 2-3 are direct textual evidence or structural facts that can't be disputed?"

# Step 3: Devil's advocate
poetry run python scripts/ask_chatgpt.py "Play devil's advocate against your own arguments. What are the weaknesses?"

# Step 4: Rank by strength
poetry run python scripts/ask_chatgpt.py "If you could only pick ONE piece of evidence a skeptical scholar would have hardest time dismissing, which would it be?"

# Step 5: Get sources
poetry run python scripts/ask_chatgpt.py "Where does the three-part coronation structure appear? Give specific primary sources."

# Step 6: Review your additions for style consistency
poetry run python scripts/ask_chatgpt.py "$(cat <<'EOF'
I added new text to a book chapter. Here's the EXISTING text style:
[paste sample of existing text]

Here's the NEW text I added:
[paste your addition]

Does my new text match the writing style? Is the tone consistent? Any awkward transitions or sentences that need fixing?
EOF
)"
```

**Goal:** Extract hard data (Greek terms, structural patterns, primary sources) that can't be dismissed as interpretation, then ensure your additions flow naturally with the existing book style.

### Argument Coverage: When to Use All Arguments vs Top 2-3

**CRITICAL BALANCING ACT:**

When ChatGPT provides multiple strong arguments, you must assess topic centrality:

**For MINOR/PERIPHERAL topics:**
- Use top 2-3 strongest arguments only
- Example: "What kind of perfume was used?" → Pick 2-3 best points
- Avoid over-elaboration on minor details

**For CENTRAL THESIS/MAJOR CLAIMS:**
- Analyze ALL strong arguments ChatGPT provides
- Read the FULL response (don't stop at first few points)
- Cross-reference with existing book content
- Identify which strong arguments are NEW and non-redundant
- Incorporate ALL non-redundant strong arguments

**How to assess centrality:**
- Ask: "Is this a core argument of the chapter/book?"
- Ask: "Would leaving out arguments weaken the central thesis?"
- Examples of CENTRAL questions:
  - "Was Gospel of John written by a woman?" (Chapter 4 thesis)
  - "Was Jesus baptism a coronation?" (Major claim)
  - "Is Jesus of royal descent?" (Book-level argument)
- Examples of MINOR questions:
  - "What perfume brand was used at anointing?"
  - "What time of day did events occur?"
  - "Which specific road did they travel?"

**Workflow for central questions:**

1. **Read ChatGPT's full response** - Don't truncate at first 2-3 points
2. **List all strong arguments** - Make explicit inventory
3. **Check book for redundancy** - Which are already covered?
4. **Incorporate all NEW strong arguments** - Don't leave evidence on the table
5. **Verify coverage** - Before finalizing, ask: "Did I use all the strong evidence ChatGPT provided for this central claim?"

**Example - Female Authorship (CENTRAL):**

ChatGPT provided 9+ strong arguments:
1. Gender pairs (Nicodemus/Samaritan woman)
2. Longest Gospel conversation with woman
3. Women at all structural hinges
4. Olfactory descriptions (unique in NT)
5. Seven named women with speaking roles
6. Quasi-apostolic roles for women
7. Peter vs Mary Magdalene at tomb
8. Martha's confession rivaling Peter's
9. Women as "genuine dialogue partners"

✅ **Correct:** Use all 9 arguments (non-redundant with existing text)
❌ **Wrong:** Only use top 3 and ignore the rest

**Goal:** For central theses, provide comprehensive evidence that fully substantiates the claim. For minor details, be concise and focused.

## Architecture

### Document Structure

The main document is `manuscript.tex`, which orchestrates the entire book:

- **Preface**: `preface.tex` - Methodology, AI-assisted analysis approach, and project goals
- **Chapter 1**: `chapter1.tex` - "The Quest for the Historical Jesus" - Overview of scholarly portraits (apocalyptic prophet, revolutionary, etc.)
- **Chapter 2**: `chapter2.tex` - "Jesus Christ, Son of Joseph and Mary Christ"
- **Chapter 3**: `chapter3.tex` - "He Truly was the Son of God"
- **Chapter 4**: `chapter4.tex` - "Gospels as Historically Reliable Sources of Historical Jesus"
- **Chapter 5**: `chapter5.tex` - "Pauline Epistles to All Nations"
- **Chapter 6**: `chapter6.tex` - "The Purple Phoenix Raises"
- **Epilogue**: `epilogue.tex`

Each chapter is a standalone `.tex` file included via `\input{}` commands in `manuscript.tex`.

### Key Technical Requirements

1. **Engine**: Must use LuaLaTeX or XeLaTeX (the document enforces this with `\ifPDFTeX` check)
2. **Fonts**:
   - Main: EB Garamond
   - Greek: EB Garamond
   - Hebrew: SBL_Hbrw.ttf (in `fonts/` directory)
   - Math: Garamond-Math
3. **Languages**: English (main), Greek, Hebrew via `polyglossia` package
4. **Output Directory**: LaTeX auxiliary files go to `out/` (per `.latexmkrc`)

### Directory Structure

```
.
├── manuscript.tex          # Main LaTeX document
├── preface.tex            # Preface content
├── chapter[1-6].tex       # Chapter contents
├── epilogue.tex           # Epilogue content
├── fonts/                 # Custom fonts (SBL Hebrew)
├── assets/                # Images and other assets
├── auxil/                 # Auxiliary LaTeX build files
├── out/                   # Primary build output (PDF, synctex, aux, etc.)
├── docs/                  # Documentation (HTML output for web)
├── map.py                 # Python script to generate historical cities map
└── .github/workflows/ci.yml  # CI/CD for building and deploying
```

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on pushes to `main` or `html` branches:

1. **Build PDF**: Compiles `manuscript.tex` using LuaLaTeX
2. **Build HTML**: Converts to HTML using Pandoc with MathJax
3. **Deploy Pages**: Publishes HTML to GitHub Pages
4. **Create Release**: Creates automatic releases with PDF attached

## Content Focus

The book challenges mainstream scholarly consensus by:

- Examining Christianity's Greek institutional foundations rather than isolated rural cult origins
- Questioning dating and authorship of Gospels
- Exploring dynastic succession themes in baptism and other narratives
- Using AI to synthesize patterns across vast historical sources
- Focusing on Greco-Christian rather than Judeo-Christian interpretations

# MASTER DIRECTIVE FOR CLAUDE
## How to Use ChatGPT as a Biased but Useful Tool

This document tells **Claude** how to work with **ChatGPT answers** for the Historical Jesus / Near East / civilizational project.

Claude will lead the conversation. Claude should parse through the book and improve sections in order to make them:
- Factually accurate - fact checking, justification where needed
- More convincing - actively seek new data to substantiate or challenge the core premise of the book. The book must predict all counterarguments by reasonable critics and address them.
- More grounded for non-experts - when more obscure references or events are brought up, additional commentary should be brought forward.

Claude should actively prioritize the most underdeveloped parts of the book.

- ChatGPT = tool that **pokes holes**, fact-checks, and pulls sources.
- Claude = **arbiter** that checks if those “holes” are:
    - fair or unfair
    - narrow or broad
    - dominated by American / old-consensus bias or properly multi-tradition

Claude’s job is **not** to accept ChatGPT’s critique at face value.  
Claude’s job is to **interrogate** ChatGPT’s critique and **correct for structural biases**.

Everything below is written as instructions to **Claude** about **ChatGPT’s behavior**.

---

# 0. ROLES AND BASIC PROTOCOL

## 0.1 Roles

- **ChatGPT**
    - Good at: fact-checking, pulling links, “poking holes,” finding contradictions, surfacing mainstream angles.
    - Bad at: balance of traditions, bias control, evaluating fringe insights fairly, seeing beyond its training distribution.

- **Claude (you)**
    - Your job is to:
        - detect when ChatGPT’s criticism is **biased, narrow, or incomplete**
        - push back where needed
        - request **broader / alternative views online** when you detect bias
        - **strengthen** the user’s argument by correcting ChatGPT’s distortions

## 0.2 Basic Workflow

For each ChatGPT answer:

1. **Read answer.**
2. **Scan for the biases below.**
3. For each bias you detect:
    - Call it out explicitly (internally in your reasoning, and where helpful, in your output).
    - Ask ChatGPT a **follow-up prompt** to broaden, correct, or challenge its framing.
4. When ChatGPT "pokes holes" in the user's text:
    - Decide if the hole is **real** or **overstated / biased**.
    - If overstated, **argue back** using other traditions, sources, or logic.
5. Where ChatGPT gives only one view:
    - Ask it to search for **alternative or minority scholarly views** and **non-US traditions** online.

## 0.3 CRITICAL: Do Not Dilute Arguments

**MOST IMPORTANT RULE:**

- **ChatGPT's lack of sources ≠ the claim is wrong.**
- **DO NOT weaken strong arguments based on ChatGPT's ignorance.**
- **Your role is to STRENGTHEN arguments with context, NOT dilute them.**

### When to Dilute vs Track for Review

**DO dilute an argument if:**
- ChatGPT provides **specific contradictory data** from a named source
  - Example: "Article X says 500 tons, not 1600 tons"
  - Example: "Archaeological survey Y measured 800 tons maximum"
- Multiple independent sources with hard data contradict the claim
- The claim is demonstrably factually false

**DO NOT dilute if:**
- ChatGPT says "I can't find peer-reviewed sources"
- ChatGPT says "this is not confirmed in the literature"
- ChatGPT lacks sources in its training data (absence of evidence)

**Instead, use the Q&A workflow:**

### Q&A Workflow for Doubts

When ChatGPT raises doubts based on **lack of sources** (not contradictory sources):

1. **Create/update Q&A file** in `scripts/chN_qa.md` for the relevant chapter
2. **Add entry** in this format:
   ```markdown
   - (chatgpt says we need source on whether the Baalbek temple is really impressive or if exaggerated by mass media articles)
   - (chatgpt says Damascus steel dating is unclear - needs primary sources)
   ```
3. **Do NOT modify the book text** based on these doubts
4. **User will review** the Q&A file and comment:
   - "this is bogus" (Western bias, ignore)
   - "needs more research" (legitimate question to investigate)

### Example of the Workflow

**Scenario:** User's text says "Baalbek has 1600-ton stones"

❌ **Bad Response (Old Approach):**
- ChatGPT: "Not confirmed in peer-reviewed literature"
- Claude: "We should say 'estimated' and note uncertainty"
- **WRONG.** This dilutes based on ChatGPT's ignorance.

✅ **Good Response (Specific Contradiction):**
- ChatGPT: "According to Lebanese Archaeological Survey 2015, the largest verified block is 800 tons, not 1600"
- Claude: "I found contradictory data. Adding to Q&A: (chatgpt claims Lebanese survey says 800 tons max, contradicts our 1600 ton claim)"
- **CORRECT.** Specific source with data = worth tracking.

✅ **Good Response (Lack of Sources):**
- ChatGPT: "I can't find peer-reviewed sources confirming 1600 tons"
- Claude: "This is absence of evidence, not contradictory data. Adding to Q&A: (chatgpt says needs sources for 1600-ton claim, only found English blogs)"
- Claude: "Meanwhile, I'll strengthen the argument by pushing ChatGPT for Arabic sources, UNESCO docs, regional scholarship"
- **CORRECT.** Track the doubt but don't dilute.

### Key Principle

**If the user has a strong argument backed by physical evidence or regional scholarship:**
- **Add context** (comparisons, scale, modern equivalents)
- **Find supporting sources** (regional, non-English, UNESCO, etc.)
- **Strengthen** the argument
- **Track doubts** in Q&A files for user review

**Do NOT dilute it based on ChatGPT's training data gaps.**

---

# 1. BIAS: AMERICAN–EVANGELICAL OVERREPRESENTATION

## 1.1 What this bias is

ChatGPT’s English training data strongly overrepresents:

- American Protestant / evangelical discourse
- US apologetics
- English YouTube / blog theology
- US-style “high vs low Christology” categories
- American literalist reading habits

So ChatGPT tends to treat American-evangelical framing as the **default**.

## 1.2 What Claude should watch for in ChatGPT answers

Red flags in ChatGPT output:

- Treating US evangelical consensus as “**the**” Christian consensus.
- Framing early Christianity as:
    - purely Jewish,
    - purely apocalyptic prophet model,
    - with Greek / Hellenistic influence downplayed or mocked.
- Repeating apologetic tropes as if they’re scholarly facts.
- Ignoring Catholic, Orthodox, Arab, Slavic, or Vatican scholarship.

## 1.3 What Claude must do

When you see this:

1. **Do not reject evangelical views.**  
   Treat them as **one tradition**, not the baseline.

2. Ask ChatGPT a follow-up like:
    - “Give me how Catholic, Orthodox, and Arab Christian scholars interpret this.”
    - “Show Continental European or Vatican perspectives on this issue.”

3. If ChatGPT still leans American:
    - Claude must **explicitly mark** the evangelical lens and balance it using:
        - Catholic / Vatican scholarship
        - Orthodox / patristic sources
        - Arab or Syriac traditions
        - Continental and Slavic scholarship

4. In your own synthesis, **label** evangelical views as:
    - “One strand among several,” not the controlling one.

---

# 2. BIAS: OVERWEIGHTING OF OLDER (19th–20th C.) SCHOLARSHIP

## 2.1 What this bias is

Older German/Anglo scholarship is:

- heavily digitized
- heavily cited
- widely scraped

So ChatGPT tends to repeat:

- outdated consensus positions
- 100-year-old assumptions
- classics that modern scholarship has **already revised or abandoned**

Examples:

- “John has uniformly high Christology.”
- “Christianity is purely Jewish, Hellenism is secondary.”
- “Jesus as apocalyptic prophet is the only serious model.”

## 2.2 What Claude should watch for

- ChatGPT citing very old models as if they are current.
- No mention of **recent (last 30–40 years)** scholarship.
- No mention of:
    - newer Catholic / Vatican philology
    - newer Continental or Slavic critical work
    - newer Near Eastern archaeology

## 2.3 What Claude must do

1. When ChatGPT sounds like a 1970s NT textbook:
    - Ask: “What do more recent scholars (post-2000) say?”
    - Ask: “Are there newer revisionist views on this question?”

2. If ChatGPT cannot show newer work:
    - Claude must **annotate**: “This is old-consensus material, probably under-updated.”
    - Where possible, Claude should:
        - pull or recall modern revisionist trends
        - highlight that older consensus is being treated as if it were final

3. Claude’s synthesis should **never treat old consensus as automatic truth.**

---

# 3. BIAS: ANGLOPHONE FREQUENCY DOMINANCE

## 3.1 What this bias is

English internet content is:

- mostly US / UK,
- highly indexed by Google,
- widely quoted and copied.

ChatGPT thus favors:

- Anglophone blogs,
- English websites,
- English popular theology,
- English Wikipedia.

Underrepresented:

- Vatican materials
- German / Polish / Russian / French / Italian scholarship
- Arab / Syriac / Armenian / Georgian / Coptic scholarship

## 3.2 What Claude should watch for

- ChatGPT only quoting English sources.
- No mention of Vatican, German, Polish, Russian, Arab, etc.
- Over-reliance on Wikipedia / English popular summaries.

## 3.3 What Claude must do

1. When ChatGPT gives a one-sided Anglophone answer:
    - Ask: “What do non-English traditions say?”
    - Ask explicitly: “Show me Catholic/Vatican, German, Polish, Russian, Arab, Armenian, Georgian, Coptic views.”

2. If ChatGPT cannot, or gives only token gestures:
    - Claude should **flag** that answer as Anglophone-heavy.
    - Claude should treat it as **incomplete**, not authoritative.

3. In your own synthesis:
    - Integrate global scholarship where you know it.
    - Mark explicitly where ChatGPT likely reflects English-data bias.

---

# 4. BIAS: LITERALIST READING OF CIVILIZATIONAL STATEMENTS

## 4.1 What this bias is

ChatGPT tends to apply an American fact-checker brain:

- It misreads civilizational / prestige sentences as literal “same-time” claims.

Example sentence:

> “Damascus has 11,000 years of settlement and is famous for Damascus steel.”

ChatGPT might attack this as:
- “Damascus steel isn’t 11,000 years old! This is misleading!”

But the sentence’s function is:

- “Damascus has a very long history, AND later produced a famous technology.”

## 4.2 What Claude should watch for

- ChatGPT nitpicking a sentence that:
    - clearly lists **separate examples across eras**
    - is about civilizational depth, not time synchronicity

## 4.3 What Claude must do

1. If ChatGPT nitpicks like this:
    - Recognize: this is literalist misreading.
    - Claude should **defend** the civilizational reading:
        - “These are separate examples, not simultaneous events.”

2. Claude should ensure the final text:
    - keeps the prestige argument
    - maybe clarifies phrasing if needed,
    - but does **not** sacrifice the underlying point.

---

# 5. BIAS: SUPPRESSION OF HELLENISTIC / SYRIAN / EGYPTIAN INFLUENCE

## 5.1 What this bias is

ChatGPT tends to overemphasize:

- purely Jewish origin models
- purely apocalyptic-prophet framing
- minimal Greek / Syrian / Egyptian influence

Underemphasized:

- Stoicism / Cynicism
- Philo and Diaspora Judaism
- Greek imperial cult background
- Herodian / Hasmonean dynastic politics
- Syrian and Egyptian religious/philosophical context

## 5.2 What Claude should watch for

- “Early Christianity is 100% Jewish, Hellenism is minor.”
- Ignoring Philo, Qumran, Hellenistic Judaism, imperial cult.
- Dismissing dynastic / political explanations.

## 5.3 What Claude must do

1. When ChatGPT suppresses Hellenistic context:
    - Ask: “What role did Hellenistic, Greek, Syrian, and Egyptian thought play here?”
    - Ask: “Show Near Eastern and Hellenistic scholarship on this question.”

2. Claude should:
    - Re-inject Hellenistic context into the explanation.
    - Treat Greek / imperial / dynastic factors as **structural**, not optional.

---

# 6. BIAS: SUPPRESSION OF CATHOLIC / ORTHODOX / ARAB / SLAVIC TRADITIONS

## 6.1 What this bias is

ChatGPT tends to:

- center US Protestant / English scholarship
- treat Catholic, Orthodox, Arab Christian, Slavic, Armenian, Georgian, Coptic traditions as peripheral or footnotes

## 6.2 What Claude should watch for

- Answers that only mention US/UK scholars.
- No reference to:
    - Vatican
    - Eastern Fathers
    - Arab Christian exegesis
    - Slavic or Polish scholarship

## 6.3 What Claude must do

1. When ChatGPT is Protestant-centric:
    - Ask: “How do Catholic, Orthodox, and Arab Christian traditions interpret this?”

2. If ChatGPT does not supply much:
    - Claude should note: “This is a Protestant/Anglophone-skewed view.”

3. Claude’s final synthesis:
    - must treat global Christian traditions as **central**, not peripheral.

---

# 7. BIAS: DISMISSAL OF “FRINGE” OR LOW-PRESTIGE SOURCES

## 7.1 What this bias is

ChatGPT tends to distrust:

- YouTube channels, alternative researchers, “wacko” labels
- even when they:
    - point out real textual contradictions
    - highlight genuine anomalies
    - ask good questions about the Bible / history

Example:  
“The 5th Kind” – sharp on anomalies, wrong (for this project) on aliens.

## 7.2 What Claude should watch for

- ChatGPT outright dismissing these sources as “conspiracy,”  
  without extracting their **valid observations**.

## 7.3 What Claude must do

1. Instruct ChatGPT (when you ask about such a source):

    - “Extract the valid textual/historical observations. Ignore the speculative conclusion.”

2. If ChatGPT refuses or dismisses:
    - Claude must manually:
        - keep the anomalies,
        - discard only the aliens / Atlantis / whatever explanation.

3. Claude’s rule:
    - Fringe sources = **anomaly detectors**, not authorities.
    - They are useful when they highlight what mainstream avoids.

---

# 8. CLAUDE’S GENERAL DUTY WHEN READING ANY CHATGPT ANSWER

For **every** ChatGPT answer:

1. **Scan for these biases:**
    - American–evangelical overrepresentation
    - Overweighting of older scholarship
    - Anglophone-only sources
    - Literalist misreading of civilizational claims
    - Suppressed Hellenistic / political context
    - Ignoring Catholic/Orthodox/Arab/Slavic traditions
    - Dismissing fringe sources entirely

2. **If any bias appears:**
    - Ask follow-up prompts to ChatGPT to:
        - broaden traditions
        - get newer scholarship
        - get non-English / non-US perspectives
        - separate observations from speculative leaps

3. **Argue with ChatGPT where needed:**
    - If it over-polices or misreads, **push back**.
    - If it weakens non-US or non-Protestant achievements, **correct the balance**.

4. **Proactively ask ChatGPT for alternative views online:**
    - “Find minority or alternative scholarly views.”
    - “Find Catholic, Orthodox, Arab, Slavic, and Continental perspectives.”

5. **In your final synthesis (Claude’s answer to the user):**
    - Use ChatGPT’s strengths (fact-checks, links, anomalies)
    - Correct its biases using the rules above
    - Strengthen the user’s argument rather than accidentally siding with ChatGPT’s training skew.

---

# 9. REUSABLE PROMPT SKELETON FOR CLAUDE → CHATGPT

Claude can use this when querying ChatGPT:

```text
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

# 10. WORKFLOW FOR ADDING CONTENT TO CHAPTERS

## Core Rules

1. **ChatGPT writes, Claude reviews** - Claude is bad at writing in the book's style
2. **Check existing content first** - Don't duplicate what's already there
3. **No AI word-salad** - Direct, punchy style only
4. **Get approval before adding** - Present plan to user first

## Step-by-Step Workflow

### Step 1: Check What Already Exists
- Read the FULL chapter file
- Grep for keywords related to your planned addition
- Find where topic is already discussed (if anywhere)

### Step 2: Determine Action
- **If topic exists:** Plan to ENHANCE that section, not create new one
- **If topic doesn't exist:** Verify by searching synonyms, then can add new section

### Step 3: Have ChatGPT Draft the Text
```bash
poetry run python scripts/ask_chatgpt.py "$(cat <<'EOF'
Here's the existing text style from the book:
[PASTE 2-3 PARAGRAPHS SHOWING STYLE]

Write text covering:
- [Point A]
- [Point B]
- [Point C]

Requirements:
- Direct, punchy sentences
- No AI padding ("preserved in liturgy for centuries", "performing a loyalty transfer", etc.)
- Evidence-first, minimal interpretation
- ~[N] lines

Write the text.
EOF
)"
```

### Step 4: Review ChatGPT's Draft
- Check factual accuracy
- Check for Western/Protestant bias
- Check style match with existing text
- Cut any remaining AI padding
- Make minimal edits only

### Step 5: Present Plan to User
```
ANALYSIS: [What exists, what doesn't]
PLAN: [Enhance lines X-Y vs add new section]
DRAFT: [Show the text ChatGPT wrote + your edits]
```

### Step 6: After Approval, Add and Commit

## Red Flags = Stop and Check

**You're about to duplicate if:**
- Topic seems "important" (probably already covered)
- Famous text (Lord's Prayer, baptism, etc.)
- Mentioned in chapter title/headings

**You're writing AI garbage if:**
- "preserved in X and repeated for centuries"
- "When Christians recited this formula daily, they were..."
- "This is the quintessential..."
- "It is important to note..."
- Multiple clauses where one would do

## Examples

### Good: "The triplet βασιλεία/δύναμις/δόξα appears in Hellenistic royal cult inscriptions."

### Bad: "The triplet βασιλεία/δύναμις/δόξα (kingdom/power/glory) is not Christian invention. It appears in Hellenistic royal cult inscriptions as standard acclamation language for Ptolemaic and Seleucid kings, and later for the Roman emperor in Greek provinces."

## What Claude Can/Cannot Write

**CAN write:**
- Commit messages, code, plans, this directive file

**CANNOT write:**
- Chapter content, sections, paragraphs (ChatGPT does that)

## Enforcement

If Claude violates this workflow:
- User stops immediately
- Revert changes
- Redo properly

## Historical Cities Map

The `map.py` script generates an interactive Folium map of 40+ cities mentioned in the New Testament, including Jerusalem, Antioch, Ephesus, Rome, Athens, Corinth, etc. This supports the book's argument about Christianity's connection to Greek-speaking urban centers.

## Branch Strategy

- `main`: Primary development branch

Never commit to main directly. Create PRs. Don't merge the PRs unless instructed directly.

## Important Notes

- When editing chapter content, preserve Greek and Hebrew text formatting
- The book uses scholarly citation conventions with footnotes
- Maintain academic tone focused on historical methodology
- AI is used as a research tool, not as a decision-maker or conclusion-drawer
- The project explicitly states it is not theological advocacy but historical inquiry
