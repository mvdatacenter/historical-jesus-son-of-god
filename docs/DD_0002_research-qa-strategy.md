# DD-0002: Alexandria Findings Pipeline

## Purpose

The Alexandria pipeline filters ~1200 extracted scholarly findings down to the ones that actually add value to the manuscript. This document specifies how that filtering works and records the failure modes that broke previous attempts.

## Known Failure Modes

### Keyword Extraction (Forbidden)

See `docs/PM_0001_keyword-extraction-fake-verification.md`. Keyword overlap between a claim and a source passage says nothing about whether the claim accurately represents the source. Words can match without meaning matching. Any mechanism that scores, ranks, or classifies citation accuracy without semantic understanding is forbidden. This prohibition applies to the concept, not just specific implementations.

### Topic-Matching for Coverage Evaluation (Forbidden)

When the book and the findings cover the same domain — which they always do — topic-level comparison produces no filtering. "Is this finding about Greek influence relevant to a book about Greek influence?" is always yes. 886 "add" findings out of ~1200 is not filtering; it is rubber-stamping.

The right question is not "Is this finding about the same topic?" but "Does the book already present this specific evidence or make this specific argument?"

**Topic-level (wrong):** "This finding is about Hellenistic royal titles. Chapter 3 discusses Hellenistic royal titles. → `new`."

**Evidence-level (right):** "This finding cites the Rosetta Stone's use of θεὸς ἐπιφανής for Ptolemy V. Chapter 3 already cites Ptolemaic 'manifest god' epithets including the Rosetta Stone at line 187. → `covered`."

The solution is coverage inventories — see Step 1 below.

## Pipeline

The `alexandria-pipelines` repo extracts findings from scholarly discourse (interviews, lectures, discussions). These findings are claims, arguments, or observations — they almost never come with formal citations. The value is in surfacing ideas and evidence the book hasn't considered.

**Critical principle:** At the filtering stage (step 1), the question is "if this claim is true, does it impact the book?" — not "is this claim well-sourced?" Source quality is irrelevant until step 3. The source material doesn't contain citations; judging findings on citation specificity is backwards.

**Note:** This is a public repo. Do not disclose specific Alexandria data sources or extraction targets in public-facing files.

Three steps. Each reduces the set; only survivors advance.

### Step 1: Coverage and Relevance Filter

**Question:** Does the book already present this specific evidence or argument? If not, does it bear on any argument the book makes?

**Model requirement.** Both inventory generation and finding evaluation MUST use the best available model (Claude Opus only). No Sonnet, no Haiku, no sub-frontier model anywhere in this step. Anything below Opus has pathetic reasoning skills — it cannot distinguish "the book cites the Rosetta Stone's θεὸς ἐπιφανής" from "the book mentions Ptolemaic epithets generally." A weaker model will silently fall back to topic-matching, which is exactly the failure mode this design exists to prevent. The cost savings from using a cheaper model are illusory: you save tokens and get 886 "add" results again.

**Context requirement.** The full chapter text MUST be read into context for both inventory generation and finding evaluation. No summaries, no truncation, no "representative excerpts." The entire point is evidence-level granularity — you cannot match against evidence you haven't read. Chapters are long but they fit in Opus context windows. There is no shortcut here.

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

The `tangential` verdict handles relevance filtering. A finding that cannot be matched to any argument in any chapter inventory is tangential by definition.

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

### Why This Order

The pipeline is ordered by cost:

| Step | Cost | Reduces set by |
|------|------|----------------|
| 1. Coverage + Relevance | Low (automated LLM pass against inventories) | ~50-70% |
| 2. Embedding | Medium (reading chapter, drafting text) | Variable |
| 3. Research | High (fact-checking, source verification) | Variable |

Filtering on source quality at step 1 would discard findings that are poorly cited but contain genuinely impactful claims. A scholar mentioning an inscription in passing, without the corpus number, may be pointing to real evidence we can track down at step 3. Discarding it at step 1 because "no specific citation" wastes the lead.

## Where Everything Lives

| What | Where |
|------|-------|
| Citation verification pipeline spec | `docs/DD_0001_citation-review-report.md` |
| Keyword extraction post-mortem | `docs/PM_0001_keyword-extraction-fake-verification.md` |
| Chapter coverage inventories | `sources/coverage/ch{N}_inventory.json` |
| Coverage + relevance verdicts | `sources/coverage_verdicts.json` |
| Coverage inventory generator | `scripts/build_coverage.py` |
| Findings review UI | `sources/extraction_review.html` |
| Review UI generator | `scripts/review_extractions.py` |
