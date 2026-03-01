# DD-0002: Alexandria Findings Pipeline

## Problem

Alexandria findings and the book cover the same domain. Topic-level filtering ("is this finding about Greek influence?") always says yes for a book about Greek influence. The first implementation produced 886 "add" findings out of ~1200 — no real filtering happened.

## Goals

1. Findings are categorized with respect to the content of the book — should they be added or are they already covered?
2. The categorization is visible in a format that makes it easy to check what was decided and why.

## Pipeline

Three steps.

**Global Q&A** (`scripts/global_qa.md`) records book-wide interpretive decisions that apply across all chapters (e.g., "mystery cult findings are reframed as imperial cult under foreign rule"). All pipeline steps consult global Q&A before per-chapter Q&A.

**Per-chapter Q&A** (`scripts/chN_qa.md`) records chapter-specific decisions, rejections, and feedback. All steps must consult both global and chapter Q&A before making decisions; without them the LLM will repeatedly resurface the same arguments.

**Research gaps** (`scripts/research_gaps.md`) is the pipeline's todo list. Claims that need investigation go here. Every item exits one of two ways: into the book, or rejected with a note in Q&A explaining why. Nothing stays in research gaps permanently.

### Step 1: Coverage and Relevance Filter

**Question:** Does the book already present this specific evidence or argument? If not, does it bear on any argument the book makes?

**Model requirement.** Both inventory generation and finding evaluation MUST use the best available model (Claude Opus only). No Sonnet, no Haiku, no sub-frontier model anywhere in this step. Anything below Opus has pathetic reasoning skills — it cannot distinguish "the book cites the Rosetta Stone's θεὸς ἐπιφανής" from "the book mentions Ptolemaic epithets generally." A weaker model will silently fall back to topic-matching, which is exactly the failure mode this design exists to prevent.

**Context requirement.** The evaluation tool (`build_coverage.py --batches`) assembles self-contained batch files. The AI does not need to remember to load inventories or chapter text — each batch includes everything.

**Batch size.** 250 findings per batch. Calculated from context window constraints:

- Opus context window: 200K tokens (~800K chars).
- Fixed context per batch: chapter text + chapter inventory + 5 cross-chapter inventories + Q&A history + anti-pattern rules. Ranges from 70K tokens (Ch1, no Q&A, short chapter) to 112K tokens (Ch4, large Q&A + large chapter text).
- Overhead for system prompt, verdict output, and safety margin: ~15K tokens.
- Average finding size: ~850 chars (~212 tokens).
- Bottleneck chapter (Ch4): 112K tokens fixed → 73K tokens remaining → max 344 findings per batch.
- 250 is conservative against the 344 ceiling, leaving ~27% headroom for larger-than-average findings and Q&A growth.
- At 250/batch: ~14 batches for the full 3,306-finding corpus.

Each evaluation context package contains:

1. **Findings to evaluate** — the findings assigned to this chapter.
2. **Target chapter inventory** — the structured inventory for the chapter being evaluated.
3. **Target chapter text** — the full chapter. No summaries, no truncation, no "representative excerpts." You cannot match against evidence you haven't read.
4. **Cross-chapter inventories** — inventories from ALL other chapters, so the evaluator can detect: (a) the finding is already covered in a different chapter, (b) the finding contradicts an argument another chapter makes, (c) the finding belongs in a different chapter.
5. **Q&A history** — the full `scripts/chN_qa.md` for the target chapter. Without this the evaluator will resurface findings that were already researched and rejected. If Q&A records a deliberate decision to exclude something, the evaluator must respect it.
6. **Anti-pattern rules** — injected verbatim (same rules as Step 2).

**Coverage inventories.** Before evaluating findings, generate a structured inventory for each chapter listing every distinct argument and every piece of specific evidence used. Not a summary — an inventory at the level of individual evidence items.

A summary is too coarse: "Chapter 3 discusses Hellenistic royal titles."
An inventory is the right granularity: "Chapter 3 argues 'Son of God' was a pre-Christian political title, citing: Alexander/Zeus-Ammon, Ptolemaic 'manifest god' epithets (Rosetta Stone), Augustus 'divi filius' coins, 4Q246, Justin Martyr Apology 1.21."

Each inventory entry has:
- **argument**: one-sentence statement of the argument
- **evidence**: list of specific evidence items (inscriptions, texts, names, dates, archaeological finds)
- **section**: where in the chapter this appears (section title or line range)

Inventories are generated once per chapter by Opus reading the full chapter text. Stored as `sources/coverage/ch{N}_inventory.json` and reused across all finding evaluations.

**Matching.** The evaluator compares each finding's specific claim and evidence against the chapter inventory. The question is: "Does this finding strengthen any argument the chapter makes?"

Not: "Does this chapter mention the same keywords as the finding?" A finding about Dionysian body-and-blood rituals belongs in the chapter that argues "Christian liturgy inherited pre-existing Greek religious practices" — even if that chapter never mentions Dionysus by name. The evaluator must understand each chapter's *arguments* and ask whether the finding provides evidence for any of them, not scan for keyword overlap.

**Anti-pattern: keyword chasing.** The most common evaluator failure is routing findings based on where their surface keywords appear rather than where their argument applies. Example: a finding about Seleucid institutional infrastructure (gymnasiums, theaters, magistracies) gets routed to whichever chapter mentions "Seleucid," when it actually belongs in the chapter that argues Greek institutional infrastructure was already present before Christianity. The finding's *framing* ("precedent for Paul's assemblies") may point to one chapter, but its *evidence* (Seleucid institutions in the Near East) may strengthen an argument in a different chapter. Evaluate the evidence, not the framing.

**Verdicts.** Every verdict must include a justification — e.g., "already in ch3 section on royal titles," "not relevant to any argument in the book," "too little evidence to act on."

- `covered` — the specific argument AND evidence are already in a chapter inventory, OR the finding was already addressed in the Q&A history (researched, incorporated, or deliberately rejected). Justification must name the chapter and section, or cite the Q&A entry. The evaluator checks ALL chapter inventories and the Q&A file (both provided in the context package), not just the assigned chapter — a finding covered in chapter 3 should not survive as "new" when assigned to chapter 5, and a finding already researched and decided in Q&A should not be resurfaced.
- `new_evidence` — the chapter makes this argument but doesn't use this specific evidence. Survives.
- `new_argument` — neither the argument nor the evidence appears in any chapter inventory. Survives.
- `contradicts` — the finding opposes an argument the book makes. Justification must name the chapter, section, and the specific argument it contradicts. Survives — the finding may be correct and the book may need revision. Flagged for user review with the contradiction made explicit.
- `wrong_chapter` — finding is relevant to the book but doesn't strengthen any argument in this chapter. Justification must (1) explain why the finding's evidence does not serve any of this chapter's arguments — not just that the chapter doesn't mention the same keywords, and (2) name the correct chapter and the specific argument there that the finding would strengthen. A finding should not be marked `wrong_chapter` simply because its topic keywords appear more frequently in another chapter. **Action:** re-chapter the finding by changing the `## Chapter N:` header in the extraction file to the correct chapter. The finding then waits for evaluation against that chapter's inventory.
- `not_relevant` — finding doesn't bear on any argument the book makes, in any chapter. Justification must say why it doesn't connect (e.g., concerns a topic the book does not address anywhere).

**Anti-patterns for `covered` verdicts.** Three failure modes observed in validation:

1. **Topic-level match.** "The book argues for Greco-Christian influence; this finding argues for Greco-Christian influence; therefore covered." Same topic is not coverage. A `covered` verdict must identify (a) the specific claim or evidence the finding brings, and (b) where the book already presents that same specific claim or evidence. If the justification cannot name both sides of the match at evidence level, the finding is not covered — it is `new_evidence` or `new_argument`.

2. **"Same argument" without evidence comparison.** "Ch1 makes this exact argument" without showing what specific evidence the finding contains versus what the book already has. A finding may bring a new scholar's framing, a new quotable authority, a new specific example, or a new angle on a known argument. If any of these are new, the finding is `new_evidence` even if the book makes a similar argument. The question is not "does the book make this argument?" but "does the book already present this specific evidence or formulation?"

3. **Implicit coverage.** "The concept is implicit in the existing framework" or "this is a variant of what's already covered" means the book does NOT state it — therefore NOT covered. Any of the following make a finding `new_evidence`, not `covered`, even if the book discusses the same topic: a named concept the book doesn't use (e.g., "competitive mythologizing," "syncreasis"), a specific mechanism the book doesn't describe (e.g., "mimesis as social identity construction"), a new scope claim (e.g., "systematic multi-source imitation across Odyssey, Iliad, and tragedies"), or a new specific source text (e.g., the book cites Mark-Homer mimesis but the finding cites Mark-Aeneid mimesis — that is a different source text, not "a variant"). The test: does the inventory already list this exact item? If the evaluator has to argue it's "implied by" or "a variant of" an existing item, it is not covered.

**Validation protocol.** Before running at scale, validate on 30 findings against one chapter:
- Build inventory for Ch3 (biggest chapter, most findings)
- Evaluate 30 findings with mixed expected outcomes
- Check that verdicts have specific justifications — not generic restatements of the verdict category
- If validation fails, the inventory granularity is wrong — fix the inventory before scaling

**Output:** `sources/coverage/ch{N}_inventory.json` (inventories), `sources/extraction_review.html` (verdicts displayed in the review UI with justifications visible per finding)

### Step 2: Embedding Attempt

**Question:** Does the book actually need this? Not every true and new statement belongs in the book.

Step 1 answers "is this new?" Step 2 answers "does adding this make the argument materially stronger?" Without this gate, every `new_evidence` finding gets written in, chapters bloat, and the book never converges.

**Process.** For each surviving finding from Step 1:

1. **Find the target section** — which section's argument does this finding serve?
2. **Read the section in context** — what evidence does it already have?
3. **Draft the text** — following the standard chapter edit workflow (ChatGPT drafts, Claude reviews). Claude does not write manuscript prose.
4. **Read the result** — is the section actually better with this addition, or just longer?
5. **Review against CLAUDE.md guidelines** — AI garbage check, evidence standards, style rules.
6. **Verdict.**

**Context injection.** The embed tool (`build_coverage.py --embed-prep`) assembles a structured context package for each surviving finding. The AI does not need to remember to load context or read rules — the tool delivers everything at the point of decision.

Each context package contains:

1. **The finding** — full text and verdict from Step 1.
2. **Anti-pattern rules** — injected verbatim (same rules as Step 1, plus the covered-verdict anti-patterns).
3. **Q&A history** — the full `scripts/chN_qa.md` for the target chapter, so the AI sees what was already researched, rejected, or flagged.
4. **Target chapter text** — the full chapter, so the AI reads the actual text rather than relying on memory or summaries.
5. **Cross-chapter inventories** — inventories from all other chapters, so the AI can see whether a deeper treatment already exists elsewhere.

This is the prevent for PM-0002: the anti-pattern rules arrive in the AI's working context as part of the tool's output, not from the AI's memory.

**Verdicts.** Every verdict must include a justification.

- `EMBED` — finding is core to an argument, substantive (a concrete text, inscription, historical fact — not just a scholar restating the thesis), and grounded enough to write now. Proceeds to Step 3 verification.
- `RESEARCH` — finding needs sourcing before it can be written. Goes to `scripts/research_gaps.md` with what source is needed and where to look. **Nothing is rejected for being "unverified" or "speculative."** ChatGPT's inability to find a source means nothing — the source may exist outside its training data. Findings that seem speculative are often the highest value because they haven't been absorbed into mainstream consensus. **This is the default verdict for any finding that is not clearly a restate, not clearly tangential, and not already rejected in Q&A.**
- `SKIP: restates` — scholar says what the book already argues in different words. The specific quote may be "new evidence" per Step 1, but adding it makes the argument longer, not stronger.
- `SKIP: tangential` — doesn't directly serve any section's argument. True but the book doesn't need it.
- `SKIP: Q&A rejected` — the Q&A file records a prior deliberate decision to exclude this finding or this class of argument. Justification must cite the specific Q&A entry.

**There is no "weak" verdict.** The evaluator does not get to reject findings based on subjective quality judgments ("too thin," "too extreme," "would weaken credibility," "contradicts consensus"). Those are editorial decisions that belong to the author. If a finding serves any argument the book makes and has not been rejected in Q&A, it is either EMBED (ready to write) or RESEARCH (needs sourcing). The evaluator's job is to assess whether the finding strengthens an argument, not whether it is "good enough."

**Data vs conclusions.** A source may provide excellent data but draw a wrong conclusion from it. The data is still valuable. Example: a mythicist speaker presents detailed parallels between early Christian initiation rites and Eleusinian mysteries — specific ritual sequences, tiered membership, secrecy oaths — then concludes "therefore Jesus never existed." The conclusion is wrong per the book's framework, but the mystery cult data directly strengthens the book's argument about Greek institutional origins. The evaluator takes the data; the author decides the conclusion. Never SKIP a finding because the source draws a wrong conclusion from good evidence.

All SKIP and RESEARCH decisions are recorded in `scripts/chN_qa.md` with the reason, so they are not resurfaced by future pipeline runs.

**CRITICAL: No finding may be rejected because ChatGPT cannot verify it.** "ChatGPT says it's unsubstantiated" is not a SKIP reason — it is a RESEARCH reason. ChatGPT lies often due to bias. It halluccinates sources, fabricates references, and presents its gaps as fact. Listen to ChatGPT, never trust it. "ChatGPT confirmed X" is a lead, not verification. "ChatGPT couldn't find X" means nothing. When a source isn't available yet, record in Q&A what's needed and where to look — the citation verification pipeline verifies, not ChatGPT.

**Q&A check.** The Q&A file is already in the context package. If it records a deliberate decision to exclude something, respect it.

**Cross-chapter check.** If another chapter contains a deeper or more developed treatment of the same argument, the new material belongs there — merged into the existing section, not duplicated. The goal is one authoritative treatment per argument, not parallel versions across chapters.

**Section-fit check.** Before inserting text into a specific section, verify: (1) the new text does not contradict the chapter's own thesis, and (2) the new text serves the argument of the section it is placed in. If the text doesn't serve the section's argument, find the section it does serve — or create one.

If the embedding would contradict existing text, surface the contradiction to the user before proceeding — one of them may be wrong, but that is a decision, not something to silently override.

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

- **Keyword extraction** for any matching or verification. See `docs/PM_0001_keyword-extraction-fake-verification.md` and `docs/PM_0002_keyword-extraction-in-embed-prep.md`. Step 2's context injection design is the structural prevent for this failure class.
- **Topic-level matching** for coverage evaluation. Same domain = no filtering. Evidence-level only.
- **Keyword chasing** for `wrong_chapter` verdicts. The evaluator must ask "does this finding strengthen any argument this chapter makes?" — not "does this chapter mention the same keywords as the finding?" A finding about Dionysian body-and-blood rituals belongs in the chapter arguing Christian liturgy inherited Greek religious practices, even if that chapter never mentions "Dionysus." A finding about Seleucid institutions belongs in the chapter arguing Greek institutional infrastructure predated Christianity, even if the finding's own framing says "precedent for Paul." Route by argument, not by keyword.
- **Sub-frontier models** for step 1. They silently degrade to topic-matching.
- **Summaries or truncated context** instead of full chapter text.
- **Trusting ChatGPT's factual assertions.** ChatGPT is a helpful research resource — use it freely to find sources and research leads. But it lies often due to bias. Listen to it, never trust it. "ChatGPT confirmed X" is a lead, not verification — download the source and run it through the pipeline. "ChatGPT couldn't find X" means nothing — the source may exist outside its training data. No KEEP/SKIP decision may rest on ChatGPT's word alone. When a source isn't available yet, record in Q&A what's needed and where to look so it can be acquired and verified.

## Where Everything Lives

| What | Where |
|------|-------|
| Chapter coverage inventories | `sources/coverage/ch{N}_inventory.json` |
| Coverage + relevance verdicts (review UI) | `sources/extraction_review.html` |
| Coverage inventory generator | `scripts/build_coverage.py` |
| Step 1 evaluation batches (with context) | `scripts/build_coverage.py --batches` |
| Step 2 embed context generator | `scripts/build_coverage.py --embed-prep` |
| Findings review UI | `sources/extraction_review.html` |
| Review UI generator | `scripts/review_extractions.py` |
| Global Q&A (book-wide decisions) | `scripts/global_qa.md` |
| Per-chapter research Q&A | `scripts/chN_qa.md` |
| Open research questions | `scripts/research_gaps.md` |
| Citation verification pipeline spec | `docs/DD_0001_citation-review-report.md` |
| Keyword extraction post-mortems | `docs/PM_0001_keyword-extraction-fake-verification.md`, `docs/PM_0002_keyword-extraction-in-embed-prep.md` |
