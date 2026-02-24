# DD-0002: Research and Quality Assurance Strategy

## Purpose

This document records the design rationale for the project's research and QA process. Operational details (scripts, file paths, commands, rules) live in the README, which is auto-appended to CLAUDE.md and available in every session.

## Design: Three Quality Gates

The project uses a two-AI model where ChatGPT generates and Claude interrogates. All work passes through three quality gates before reaching the manuscript:

1. **Generation** — ChatGPT produces research, arguments, and prose
2. **Review** — Claude reviews every non-trivial output for accuracy and style
3. **Verification** — Citation claims are checked against downloaded source texts

No single gate is sufficient alone. Generation without review produces hallucinations. Review without verification leaves citation accuracy unchecked. Verification without review catches wrong sources but not wrong arguments.

## Why Three Gates

The three-gate model exists because each gate catches a different failure mode:

- **Gate 1 (generation)** controls input quality via bias-aware prompting. Without it, ChatGPT defaults to American-Evangelical, Anglophone, and old-scholarship biases. The seven known biases are documented in README > WORKING WITH CHATGPT > Bias Detection Reference.

- **Gate 2 (review)** catches hallucinations, filler, and coherence collapse. ChatGPT exhibits unpredictable quality degradation that it cannot self-detect. The risk-level escalation system ensures review effort scales with claim importance. See README > AI GOVERNANCE.

- **Gate 3 (verification)** catches citation inaccuracy — claims that are well-written and plausible but misrepresent what the source actually says. This is the hardest failure mode to catch because it requires reading both the manuscript claim and the source passage. See README > CITATION VERIFICATION and `docs/DD_0001_citation-review-report.md`.

## Why Keyword Extraction is Permanently Forbidden

See `docs/PM_0001_keyword-extraction-fake-verification.md` for the full post-mortem. The core lesson: keyword overlap between a claim and a source passage says nothing about whether the claim accurately represents the source. Words can match without meaning matching. Low overlap does not mean the claim is wrong. Any automated scoring system substitutes string matching for semantic judgment and produces false confidence.

This prohibition applies to the concept, not just specific function names. Any mechanism that scores, ranks, or classifies citation accuracy without semantic understanding is forbidden.

## Why Topic-Matching Fails for Coverage Evaluation

When the book and the findings cover the same domain — which they always do, since Alexandria extracts findings about early Christianity for a book about early Christianity — topic-level comparison produces no filtering. "Is this finding about Greek influence relevant to a book about Greek influence?" is always yes. 886 "add" findings out of ~1200 is not filtering; it is rubber-stamping.

The right question is not "Is this finding about the same topic?" but "Does the book already present this specific evidence or make this specific argument?"

**Topic-level comparison:** "This finding is about Hellenistic royal titles. Chapter 3 discusses Hellenistic royal titles. → `new` (the finding adds to the topic)."

**Evidence-level comparison:** "This finding cites the Rosetta Stone's use of θεὸς ἐπιφανής for Ptolemy V. Chapter 3 already cites Ptolemaic 'manifest god' epithets including the Rosetta Stone at line 187. → `covered`."

The solution is coverage inventories: structured lists of every distinct argument and every piece of specific evidence in each chapter, at the granularity of individual evidence items. Matching happens against the inventory, not against topic summaries.

## Alexandria: Extended Research Materials

The `alexandria-pipelines` repo is the project's extended research corpus. It uses knowledge extraction pipelines to surface scholarly insights from unstructured sources that are not well-indexed by search engines or well-represented in LLM training data.

**Note:** This is a public repo. The specific data sources and extraction targets used by Alexandria are proprietary. Do not disclose them in public-facing documentation.

### Alexandria Findings Pipeline

Alexandria extracts findings from scholarly discourse (interviews, lectures, discussions). These findings are claims, arguments, or observations made by scholars — they almost never come with formal citations attached. This is by design: the value is in surfacing ideas and evidence that the book hasn't considered, not in providing pre-packaged citations.

**Critical principle:** At the filtering stage (step 1), the question is "if this claim is true, does it impact the book?" — not "is this claim well-sourced?" Source quality is irrelevant until step 3. Judging extracted findings on citation specificity is backwards because the source material doesn't contain citations.

The pipeline has three steps. Each step reduces the set of findings; only survivors advance.

#### Step 1: Coverage and Relevance Filter (automated)

**Question:** Does the book already present this specific evidence or argument? If not, does it bear on any argument the book makes?

This step combines coverage filtering and relevance filtering into a single pass using coverage inventories.

**Model requirement.** Both inventory generation and finding evaluation MUST use the best available model (Claude Opus only). No Sonnet, no Haiku, no sub-frontier model anywhere in this step. Anything below Opus has pathetic reasoning skills — it cannot distinguish "the book cites the Rosetta Stone's θεὸς ἐπιφανής" from "the book mentions Ptolemaic epithets generally." A weaker model will silently fall back to topic-matching, which is exactly the failure mode this design exists to prevent. The cost savings from using a cheaper model are illusory: you save tokens and get 886 "add" results again.

**Context requirement.** The full chapter text MUST be read into context for both inventory generation and finding evaluation. No summaries, no truncation, no "representative excerpts." The entire point is evidence-level granularity — you cannot match against evidence you haven't read. Chapters are long but they fit in Opus context windows. There is no shortcut here.

**Coverage inventories.** Before evaluating findings, generate a structured inventory for each chapter listing every distinct argument and every piece of specific evidence used. Not a summary — an inventory at the level of individual evidence items.

A summary is too coarse: "Chapter 3 discusses Hellenistic royal titles."
An inventory is the right granularity: "Chapter 3 argues 'Son of God' was a pre-Christian political title, citing: Alexander/Zeus-Ammon, Ptolemaic 'manifest god' epithets (Rosetta Stone), Augustus 'divi filius' coins, 4Q246, Justin Martyr Apology 1.21."

Each inventory entry has:
- **argument**: one-sentence statement of the argument
- **evidence**: list of specific evidence items (inscriptions, texts, names, dates, archaeological finds)
- **section**: where in the chapter this appears (section title or line range)

Inventories are generated once per chapter by an LLM reading the full chapter text. They are stored as JSON files (`sources/coverage/ch{N}_inventory.json`) and reused across all finding evaluations.

**Matching.** For each finding, the evaluator compares the finding's specific claim and evidence against the chapter inventory. The matching question is: "Is the specific evidence or argument in this finding already present in the chapter's inventory?"

**Verdicts:**
- `covered` — the specific argument AND evidence are already in the chapter inventory. Discard.
- `new_evidence` — the chapter makes this argument but doesn't use this specific evidence. Survives.
- `new_argument` — neither the argument nor the evidence appears in any chapter inventory. Survives.
- `tangential` — related to the book's themes but doesn't bear on any inventoried argument. Discard.

The `tangential` verdict replaces the old separate relevance filter. A finding that cannot be matched to any argument in any chapter inventory is tangential by definition — no separate step needed.

**Validation protocol.** Before running at scale, validate on 30 findings against one chapter:
- Build inventory for Ch3 (biggest chapter, most findings)
- Evaluate 30 findings with mixed expected outcomes
- Success criteria: generic restated findings → `covered`, specific new evidence → `new_evidence`, at least 40% of test findings filtered out
- If validation fails, the inventory granularity is wrong — fix the inventory before scaling

**Output:** `sources/coverage/ch{N}_inventory.json` (inventories), `sources/coverage_verdicts.json` (verdicts)

#### Step 2: Embedding Attempt

**Question:** Does this finding genuinely add value when placed in the book?

For each surviving finding, attempt to integrate it into the manuscript at the specific location where it would strengthen the argument. This is where the finding meets the actual text.

If the finding clearly adds value — a new piece of evidence, a stronger formulation, a counter-argument that needs addressing — proceed to step 3.

If uncertain whether the finding adds value, discuss with ChatGPT: paste the surrounding manuscript text + the finding, ask whether the argument is genuinely strengthened or just made longer.

**This step follows the standard chapter edit workflow** (see README > Core Workflow for Adding Content to Chapters). ChatGPT drafts the integration; Claude reviews.

#### Step 3: Research and Verification

**Question:** Is the claim factually accurate?

Only now — after confirming the finding is relevant and adds value — do we invest effort in verifying the claim. Use ChatGPT to research:

- Is the claimed text/inscription/event real?
- Does the primary source actually say what the finding claims?
- Are there known counter-arguments or refutations?

**Three outcomes:**

1. **Claim verified** — The evidence checks out. Pass to the standard review process (Claude review → citation verification pipeline).
2. **Claim uncertain but valuable** — The evidence can't be fully confirmed but the argument is strong enough to keep with appropriate scholarly caveat (e.g., "if X is authentic..." or qualifying language). Decision is human.
3. **Claim false or unsupported** — Remove from manuscript.

### Why This Order Matters

Research is expensive. The pipeline is ordered by cost:

| Step | Cost | Reduces set by |
|------|------|----------------|
| 1. Coverage + Relevance | Low (automated LLM pass against inventories) | ~50-70% |
| 2. Embedding | Medium (requires reading chapter, drafting text) | Variable |
| 3. Research | High (fact-checking, source verification) | Variable |

Filtering on source quality at step 1 would discard findings that are poorly cited but contain genuinely impactful claims. A scholar mentioning an inscription in passing, without giving the corpus number, may be pointing to real evidence that we can track down at step 3. Discarding it at step 1 because "no specific citation" wastes the lead.

### Interaction with Three Quality Gates

The Alexandria pipeline is a **pre-processing funnel** that feeds into the existing three-gate system. Steps 2-3 of the Alexandria pipeline overlap with Gate 1 (generation) and Gate 2 (review). Once a finding passes step 3, it enters the standard citation verification pipeline (Gate 3).

## Where Everything Lives

| What | Where |
|------|-------|
| Process rules (AI governance, evidence standards, writing standards) | README > respective sections |
| Research tracking files and conventions | README > WORKING WITH CHATGPT > Research Tracking |
| Citation verification pipeline | README > CITATION VERIFICATION |
| Script reference | README > PROJECT SETUP > Toolchain Reference |
| File conventions | README > PROJECT SETUP > File Conventions |
| Citation pipeline technical spec | `docs/DD_0001_citation-review-report.md` |
| Keyword extraction post-mortem | `docs/PM_0001_keyword-extraction-fake-verification.md` |
| Chapter coverage inventories (step 1) | `sources/coverage/ch{N}_inventory.json` |
| Alexandria coverage + relevance verdicts (step 1) | `sources/coverage_verdicts.json` |
| Coverage inventory generator | `scripts/build_coverage.py` |
| Alexandria findings review UI | `sources/extraction_review.html` |
| Review UI generator | `scripts/review_extractions.py` |
