# DD-0002: Alexandria Findings Pipeline

## Problem

Alexandria findings and the book cover the same domain. Topic-level filtering ("is this finding about Greek influence?") always says yes for a book about Greek influence. The first implementation produced 886 "add" findings out of ~1200 — no real filtering happened.

## Goals

1. Findings are categorized with respect to the content of the book — should they be added or are they already covered?
2. The categorization is visible in a format that makes it easy to spot-check results and iterate on the process.

## Non-goals

- Source verification. Findings from scholarly discourse lack citations by design; factual accuracy is checked downstream.
- Automating manuscript edits. Embedding findings is a human + ChatGPT workflow.

## Pipeline

Three steps. Each reduces the set; only survivors advance. Ordered by cost — cheap filtering first, expensive verification last.

| Step | Cost | Reduces set by |
|------|------|----------------|
| 1. Coverage + Relevance | Low (automated LLM pass against inventories) | ~50-70% |
| 2. Embedding | Medium (reading chapter, drafting text) | Variable |
| 3. Research | High (fact-checking, source verification) | Variable |

### Step 1: Coverage and Relevance Filter

**Question:** Does the book already present this specific evidence or argument? If not, does it bear on any argument the book makes?

**Model requirement.** Both inventory generation and finding evaluation MUST use the best available model (Claude Opus only). No Sonnet, no Haiku, no sub-frontier model anywhere in this step. Anything below Opus has pathetic reasoning skills — it cannot distinguish "the book cites the Rosetta Stone's θεὸς ἐπιφανής" from "the book mentions Ptolemaic epithets generally." A weaker model will silently fall back to topic-matching, which is exactly the failure mode this design exists to prevent.

**Context requirement.** The full chapter text MUST be read into context for both inventory generation and finding evaluation. No summaries, no truncation, no "representative excerpts." You cannot match against evidence you haven't read.

**Coverage inventories.** Before evaluating findings, generate a structured inventory for each chapter listing every distinct argument and every piece of specific evidence used. Not a summary — an inventory at the level of individual evidence items.

A summary is too coarse: "Chapter 3 discusses Hellenistic royal titles."
An inventory is the right granularity: "Chapter 3 argues 'Son of God' was a pre-Christian political title, citing: Alexander/Zeus-Ammon, Ptolemaic 'manifest god' epithets (Rosetta Stone), Augustus 'divi filius' coins, 4Q246, Justin Martyr Apology 1.21."

Each inventory entry has:
- **argument**: one-sentence statement of the argument
- **evidence**: list of specific evidence items (inscriptions, texts, names, dates, archaeological finds)
- **section**: where in the chapter this appears (section title or line range)

Inventories are generated once per chapter by Opus reading the full chapter text. Stored as `sources/coverage/ch{N}_inventory.json` and reused across all finding evaluations.

**Matching.** The evaluator compares each finding's specific claim and evidence against the chapter inventory. The question: "Is the specific evidence or argument in this finding already present in the chapter's inventory?"

**Verdicts:**
- `covered` — the specific argument AND evidence are already in the chapter inventory. Discard.
- `new_evidence` — the chapter makes this argument but doesn't use this specific evidence. Survives.
- `new_argument` — neither the argument nor the evidence appears in any chapter inventory. Survives.
- `tangential` — related to the book's themes but doesn't bear on any inventoried argument. Discard.

**Validation protocol.** Before running at scale, validate on 30 findings against one chapter:
- Build inventory for Ch3 (biggest chapter, most findings)
- Evaluate 30 findings with mixed expected outcomes
- Success criteria: generic restated findings → `covered`, specific new evidence → `new_evidence`, at least 40% filtered out
- If validation fails, the inventory granularity is wrong — fix the inventory before scaling

**Output:** `sources/coverage/ch{N}_inventory.json` (inventories), `sources/coverage_verdicts.json` (verdicts)

### Step 2: Embedding Attempt

**Question:** Does this finding genuinely add value when placed in the book?

For each surviving finding, attempt to integrate it into the manuscript where it would strengthen the argument. If the finding clearly adds value — new evidence, a stronger formulation, a counter-argument that needs addressing — proceed to step 3. If uncertain, discuss with ChatGPT: paste the surrounding manuscript text + the finding, ask whether the argument is genuinely strengthened or just made longer.

This step follows the standard chapter edit workflow (README > Core Workflow for Adding Content to Chapters). ChatGPT drafts; Claude reviews.

### Step 3: Research and Verification

**Question:** Is the claim factually accurate?

Only after confirming the finding is relevant and adds value do we invest in verification. Use ChatGPT to research:

- Is the claimed text/inscription/event real?
- Does the primary source actually say what the finding claims?
- Are there known counter-arguments or refutations?

**Three outcomes:**

1. **Verified** — Evidence checks out. Pass to standard review process (Claude review → citation verification pipeline).
2. **Uncertain but valuable** — Can't fully confirm but argument is strong enough to keep with scholarly caveat. Human decision.
3. **False or unsupported** — Remove from manuscript.

## Forbidden Approaches

- **Keyword extraction** for any matching or verification. See `docs/PM_0001_keyword-extraction-fake-verification.md`.
- **Topic-level matching** for coverage evaluation. Same domain = no filtering. Evidence-level only.
- **Sub-frontier models** for step 1. They silently degrade to topic-matching.
- **Summaries or truncated context** instead of full chapter text.

## Where Everything Lives

| What | Where |
|------|-------|
| Chapter coverage inventories | `sources/coverage/ch{N}_inventory.json` |
| Coverage + relevance verdicts | `sources/coverage_verdicts.json` |
| Coverage inventory generator | `scripts/build_coverage.py` |
| Findings review UI | `sources/extraction_review.html` |
| Review UI generator | `scripts/review_extractions.py` |
| Citation verification pipeline spec | `docs/DD_0001_citation-review-report.md` |
| Keyword extraction post-mortem | `docs/PM_0001_keyword-extraction-fake-verification.md` |
