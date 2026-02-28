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

**Model requirement.** Evaluation MUST use the best available model (Claude Opus only). No Sonnet, no Haiku, no sub-frontier model anywhere in this step. Anything below Opus has pathetic reasoning skills — it cannot distinguish "the book cites the Rosetta Stone's θεὸς ἐπιφανής" from "the book mentions Ptolemaic epithets generally." A weaker model will silently fall back to topic-matching, which is exactly the failure mode this design exists to prevent. This was validated empirically: Haiku wrote a keyword-matching script (98% covered, 0% new_evidence), Sonnet hallucinated 99/100 finding IDs. Only Opus performed real evidence-level matching.

**One call per chapter — no batching.** Each chapter's full text plus all its findings fit within Opus's context window (largest case: Ch2 at ~123K tokens out of 200K available). The evaluator reads the full chapter text and all findings in a single call. No batching, no inventory intermediary, no re-reading shared context across multiple calls.

**Match against full chapter text, not summaries.** The model reads the actual LaTeX source of the chapter and matches each finding's specific evidence against what the chapter actually says. No coverage inventories, no pre-digested summaries, no intermediate representations. You cannot match against evidence you haven't read, and any summary risks losing the specific details that make evidence-level matching possible.

**Other-chapter summaries for routing.** The evaluator also reads `sources/coverage/chapter_summaries.md`, which lists the core arguments of every chapter. This is NOT used for matching (matching is always against the full chapter text). It is used solely to distinguish `wrong_chapter` from `not_relevant`: when a finding doesn't match the current chapter, the evaluator checks whether it matches any other chapter's arguments before marking it irrelevant. Without these summaries, the evaluator tends to mark findings as `not_relevant` when they are actually relevant to another chapter — silently discarding material that should be re-routed.

**Matching.** The evaluator compares each finding's specific claim and evidence against the chapter text. The question: "Is the specific evidence or argument in this finding already present in the chapter?"

**Verdicts.** Every verdict must include a justification — e.g., "already in ch3 section on royal titles," "not relevant to any argument in the book," "too little evidence to act on."

- `covered` — the specific argument AND evidence are already in the chapter text. Justification must name the section.
- `new_evidence` — the chapter makes this argument but doesn't use this specific evidence. Survives.
- `new_argument` — neither the argument nor the evidence appears anywhere in the chapter. Survives.
- `wrong_chapter` — finding is relevant to the book but doesn't bear on any argument in this chapter. Justification must name the correct chapter. **Action:** re-chapter the finding by changing the `## Chapter N:` header in the extraction file to the correct chapter. The finding then waits for evaluation against that chapter.
- `not_relevant` — finding doesn't bear on any argument the book makes, **in any chapter**. Before assigning this verdict, the evaluator MUST check the chapter summaries to confirm no chapter covers this topic. Justification must say why it doesn't connect to any chapter (e.g., concerns a topic the book does not address anywhere). This verdict should be extremely rare — the book covers a wide scope.

**Output:** `sources/extraction_review.html` (verdicts displayed in the review UI with justifications visible per finding)

#### Wrong-Chapter Redistribution Loop

Findings that receive a `wrong_chapter` verdict are relevant to the book but were evaluated against the wrong chapter. These are redistributed to the correct chapter and re-evaluated in an iterative loop until convergence.

**Redistribution command:**

```bash
python scripts/build_coverage.py --redistribute              # Round 1
python scripts/build_coverage.py --redistribute --round 2    # Round 2+
```

**Round 1** scans all `ch{N}_verdicts_opus_*.json` files (main evaluation) for `wrong_chapter` entries. **Round 2+** scans only the previous round's redistribution verdict files (`ch{N}_verdicts_opus_redistrib_r{N-1}.json`).

**Target chapter parsing** extracts the correct chapter from three verdict formats:
1. Explicit `suggested_chapter` field (int or string like `"ch5"`)
2. Regex `Chapter N` in `justification` text
3. Regex `Chapter N` in `rationale` text

**Output files:** `sources/coverage/ch{N}_findings_redistrib_r{R}.json` — batch files for evaluation agents, containing `{finding_id, text, quote, source_chapter}`.

**Evaluation agents** process these batch files and write verdicts to `ch{N}_verdicts_opus_redistrib_r{R}.json`.

**Convergence loop:**
1. Run `--redistribute --round 1` → produces batch files
2. Launch evaluation agents on the batch files
3. Agents write verdict files
4. Run `--redistribute --round 2` — if zero new `wrong_chapter`, converged
5. Repeat until convergence or max 3 rounds

**Safety mechanisms:**
- Maximum 3 redistribution rounds (hard cap)
- Ping-pong detection: if a finding receives `wrong_chapter` in 2 consecutive rounds, it is flagged for manual review instead of being redistributed again

### Step 2: Embedding Attempt

**Question:** Does this finding genuinely add value when placed in the book?

**Q&A check.** Before attempting to embed a finding, read the relevant `scripts/chN_qa.md`. A finding may have already been rejected for a specific reason, or the claim may already have been verified through a different path. The book does not need to address every counterargument to every criticism — if Q&A records show a deliberate decision to exclude something, respect it.

**Cross-chapter check.** Before writing any text into a chapter, grep all chapter files for the topic. If the book already addresses this topic elsewhere, read that section. If the embedding would contradict existing text, surface the contradiction to the user before proceeding — one of them may be wrong, but that is a decision, not something to silently override by writing a competing version.

If another chapter already contains a deeper or more developed treatment of the same argument, the new material belongs there — merged into the existing section, not duplicated in a second location. A finding assigned to Chapter N in Step 1 may turn out to strengthen an argument that Chapter M already develops in depth. In that case, embed it in Chapter M, not Chapter N. The goal is one authoritative treatment per argument, not parallel versions across chapters.

**Section-fit check.** Before inserting text into a specific section, verify two things: (1) the new text does not contradict the chapter's own thesis, and (2) the new text serves the argument of the section it is placed in. A finding about authorship attribution does not belong in a section arguing about dating, even if both are in the same chapter. If the text doesn't serve the section's argument, find the section it does serve — or create one.

**Manuscript prose.** All text written into a chapter must go through the standard chapter edit workflow: ChatGPT drafts the text, Claude reviews. Claude does not write manuscript prose.

For each surviving finding, attempt to integrate it into the manuscript where it would strengthen the argument. If the finding clearly adds value — new evidence, a stronger formulation, a counter-argument that needs addressing — proceed to step 3. If uncertain, discuss with ChatGPT: paste the surrounding manuscript text + the finding, ask whether the argument is genuinely strengthened or just made longer.

**ChatGPT is helpful for discussing editorial value** ("does this make the argument stronger or just longer?") and for research leads ("where might this claim come from?"). But ChatGPT lies often due to bias — it hallucinates sources, fabricates references, and presents its gaps as fact. Listen to ChatGPT, but never trust it.

**No KEEP or SKIP decision may rest on ChatGPT's factual assertions alone.** If ChatGPT says a claim checks out, that is a useful lead — now verify through the citation verification pipeline: download the source, search the text, present side-by-side. If ChatGPT can't find something, that means nothing — the source may exist outside its training data. When a source isn't in the registry yet, add it to `scripts/source_registry.py` and record in Q&A what source is needed and where to look, so it can be downloaded and verified through the pipeline.

This step follows the standard chapter edit workflow (README > Core Workflow for Adding Content to Chapters). ChatGPT drafts; Claude reviews.

**Step 2 produces draft text, not committed text.** Embeddings are written to the chapter file but NOT committed until Step 3 verification is complete. Step 2 ends with uncommitted edits in the working tree and a list of claims that need verification. The commit happens after Step 3, and the commit message must reference which claims were verified and how (e.g., "verified Vaticanus ends at 16:8 via facsimile," "Tertullian attribution confirmed in Adv. Prax. 27").

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
- **Sub-frontier models** for step 1. They silently degrade to topic-matching. Validated: Haiku keyword-matched, Sonnet hallucinated IDs, only Opus worked.
- **Summaries, inventories, or truncated context** instead of full chapter text. Every chapter + all its findings fit in a single Opus call. There is no reason to use an intermediate representation.
- **Batching** findings into multiple calls per chapter. Re-reading shared context across batches wastes tokens and introduces consistency risk.
- **Trusting ChatGPT's factual assertions.** ChatGPT is a helpful research resource — use it freely to find sources and research leads. But it lies often due to bias. Listen to it, never trust it. "ChatGPT confirmed X" is a lead, not verification — download the source and run it through the pipeline. "ChatGPT couldn't find X" means nothing — the source may exist outside its training data. No KEEP/SKIP decision may rest on ChatGPT's word alone. When a source isn't available yet, record in Q&A what's needed and where to look so it can be acquired and verified.

## Where Everything Lives

| What | Where |
|------|-------|
| Coverage + relevance verdicts (review UI) | `sources/extraction_review.html` |
| Findings review UI | `sources/extraction_review.html` |
| Review UI generator | `scripts/review_extractions.py` |
| Chapter argument summaries (for routing) | `sources/coverage/chapter_summaries.md` |
| Coverage evaluation runner | `scripts/build_coverage.py` |
| Redistribution batch files | `sources/coverage/ch{N}_findings_redistrib_r{R}.json` |
| Redistribution verdict files | `sources/coverage/ch{N}_verdicts_opus_redistrib_r{R}.json` |
| Per-chapter research Q&A | `scripts/chN_qa.md` |
| Open research questions | `scripts/research_gaps.md` |
| Citation verification pipeline spec | `docs/DD_0001_citation-review-report.md` |
| Keyword extraction post-mortem | `docs/PM_0001_keyword-extraction-fake-verification.md` |
| Model comparison test data | `sources/coverage/model_comparison_*.json` |
