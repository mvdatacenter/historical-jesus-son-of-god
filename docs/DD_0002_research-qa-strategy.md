# DD-0002: Alexandria Findings Pipeline

## Problem

Alexandria findings and the book cover the same domain. Topic-level filtering ("is this finding about Greek influence?") always says yes for a book about Greek influence. The first implementation produced 886 "add" findings out of ~1200 — no real filtering happened.

## Goals

1. Findings are categorized with respect to the content of the book — should they be added or are they already covered?
2. The categorization is visible in a format that makes it easy to check what was decided and why.

## Pipeline

Three steps.

**Q&A files** (`scripts/chN_qa.md`) record what was already researched — decisions, rejections, and feedback that is not in the book. All steps must consult them before making decisions; without them the LLM will repeatedly resurface the same arguments.

**Research gaps** (`scripts/research_gaps.md`) is the pipeline's todo list. Claims that need investigation go here. Every item exits one of two ways: into the book, or rejected with a note in Q&A explaining why. Nothing stays in research gaps permanently.

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

**Verdicts.** Every verdict must include a justification — e.g., "already in ch3 section on royal titles," "not relevant to any argument in the book," "too little evidence to act on."

- `covered` — the specific argument AND evidence are already in the chapter inventory. Justification must name the chapter and section.
- `new_evidence` — the chapter makes this argument but doesn't use this specific evidence. Survives.
- `new_argument` — neither the argument nor the evidence appears in any chapter inventory. Survives.
- `wrong_chapter` — finding is relevant to the book but doesn't bear on any argument in this chapter. Justification must name the correct chapter. **Action:** re-chapter the finding by changing the `## Chapter N:` header in the extraction file to the correct chapter. The finding then waits for evaluation against that chapter's inventory.
- `not_relevant` — finding doesn't bear on any argument the book makes, in any chapter. Justification must say why it doesn't connect (e.g., contradicts the book's thesis, concerns a topic the book does not address anywhere).

**Validation protocol.** Before running at scale, validate on 30 findings against one chapter:
- Build inventory for Ch3 (biggest chapter, most findings)
- Evaluate 30 findings with mixed expected outcomes
- Check that verdicts have specific justifications — not generic restatements of the verdict category
- If validation fails, the inventory granularity is wrong — fix the inventory before scaling

**Output:** `sources/coverage/ch{N}_inventory.json` (inventories), `sources/extraction_review.html` (verdicts displayed in the review UI with justifications visible per finding)

### Step 2: Embedding Attempt

**Question:** Does this finding genuinely add value when placed in the book?

**Q&A check.** Before attempting to embed a finding, read the relevant `scripts/chN_qa.md`. A finding may have already been rejected for a specific reason, or the claim may already have been verified through a different path. The book does not need to address every counterargument to every criticism — if Q&A records show a deliberate decision to exclude something, respect it.

For each surviving finding, attempt to integrate it into the manuscript where it would strengthen the argument. If the finding clearly adds value — new evidence, a stronger formulation, a counter-argument that needs addressing — proceed to step 3. If uncertain, discuss with ChatGPT: paste the surrounding manuscript text + the finding, ask whether the argument is genuinely strengthened or just made longer.

**ChatGPT is helpful for discussing editorial value** ("does this make the argument stronger or just longer?") and for research leads ("where might this claim come from?"). But ChatGPT lies often due to bias — it hallucinates sources, fabricates references, and presents its gaps as fact. Listen to ChatGPT, but never trust it.

**No KEEP or SKIP decision may rest on ChatGPT's factual assertions alone.** If ChatGPT says a claim checks out, that is a useful lead — now verify through the citation verification pipeline: download the source, search the text, present side-by-side. If ChatGPT can't find something, that means nothing — the source may exist outside its training data. When a source isn't in the registry yet, add it to `scripts/source_registry.py` and record in Q&A what source is needed and where to look, so it can be downloaded and verified through the pipeline.

This step follows the standard chapter edit workflow (README > Core Workflow for Adding Content to Chapters). ChatGPT drafts; Claude reviews.

### Step 3: Research and Verification

**Question:** Is the claim factually accurate?

**Q&A check.** Before researching a claim, read the relevant `scripts/chN_qa.md`. The claim may already be verified, marked bogus, or flagged as needing specific follow-up. A finding marked "uncertain" in Step 2 may already have a resolution in Q&A. Claims that were researched and rejected stay rejected — record the rejection reason in `scripts/research_gaps.md` so it is not revisited.

Only after confirming the finding is relevant and adds value do we invest in verification.

**Verification uses the established citation verification pipeline** (`docs/DD_0001_citation-review-report.md`). ChatGPT is a helpful research assistant for finding sources and pointing to scholarly debates, but it lies often and must never be trusted as the final word. Listen to ChatGPT, then verify independently.

**Verification hierarchy (in order of authority):**

1. **Primary source text** — Read the actual ancient text. This is the only real verification.
2. **Citation verification pipeline** — For texts in the source registry, use the download + side-by-side review pipeline.
3. **ChatGPT as research lead** — ChatGPT helps locate sources and identify debates. Its answers are starting points, never endpoints. "ChatGPT confirmed it" is not verification. "ChatGPT couldn't find it" is not refutation.

**Three outcomes:**

1. **Verified against primary source** — Evidence checks out in the actual text. Pass to standard review process (Claude review → citation verification pipeline).
2. **Uncertain but valuable** — Source not yet downloaded or not publicly available. Record in Q&A what source is needed and where to look, add to source registry if possible. Stays in pipeline until source is acquired and checked.
3. **False or unsupported** — Primary source contradicts the claim, or claim is demonstrably fabricated. Remove from manuscript. Record rejection in Q&A with the specific counter-evidence.

## Forbidden Approaches

- **Keyword extraction** for any matching or verification. See `docs/PM_0001_keyword-extraction-fake-verification.md`.
- **Topic-level matching** for coverage evaluation. Same domain = no filtering. Evidence-level only.
- **Sub-frontier models** for step 1. They silently degrade to topic-matching.
- **Summaries or truncated context** instead of full chapter text.
- **Trusting ChatGPT's factual assertions.** ChatGPT is a helpful research resource — use it freely to find sources and research leads. But it lies often due to bias. Listen to it, never trust it. "ChatGPT confirmed X" is a lead, not verification — download the source and run it through the pipeline. "ChatGPT couldn't find X" means nothing — the source may exist outside its training data. No KEEP/SKIP decision may rest on ChatGPT's word alone. When a source isn't available yet, record in Q&A what's needed and where to look so it can be acquired and verified.

## Where Everything Lives

| What | Where |
|------|-------|
| Chapter coverage inventories | `sources/coverage/ch{N}_inventory.json` |
| Coverage + relevance verdicts (review UI) | `sources/extraction_review.html` |
| Coverage inventory generator | `scripts/build_coverage.py` |
| Findings review UI | `sources/extraction_review.html` |
| Review UI generator | `scripts/review_extractions.py` |
| Per-chapter research Q&A | `scripts/chN_qa.md` |
| Open research questions | `scripts/research_gaps.md` |
| Citation verification pipeline spec | `docs/DD_0001_citation-review-report.md` |
| Keyword extraction post-mortem | `docs/PM_0001_keyword-extraction-fake-verification.md` |
