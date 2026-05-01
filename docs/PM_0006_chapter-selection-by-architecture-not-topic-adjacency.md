# PM-0006: Chapter Selection by Architecture, Not Topic-Adjacency

## What Happened

PR #112 added a paragraph to chapter 3 of `historical-jesus-son-of-god` placing the Lazarus parable in conversation with the demotic Egyptian Setne II cycle (source-criticism of a Gospel parable). Chapter 3's argumentative job is title-theology — establishing what "Son of God" meant as Greek-Egyptian royal-divine titulature. Source-criticism of Gospel parables and Gospels-to-cities geographic placement are chapter 5 territory, not chapter 3.

The AI selected chapter 3 because chapter 3 line 136 already mentioned the Lazarus-and-rich-man parable as anthropology evidence. The AI took that local mention as the placement signal and added source-critical content on top. The AI followed `CLAUDE.md` "Core Workflow for Adding Content to Chapters" Step 1 ("Read full chapter + grep for keywords → Find where topic already exists") correctly. The workflow is what produced the wrong outcome.

The same session produced PR #111 (already merged): Egyptian-transformation-theology in chapter 4. Chapter 4's argumentative job is Gospel reliability via authorship arguments; the John–Alexandria geographic link belongs in chapter 5. PR #111 may also be misplaced; audit pending.

The trace of the chapter-selection decision: user said "put Thread A in the book"; AI grepped for "Lazarus" across chapters; found a local mention at chapter 3 line 136; read chapter 3 in full; chose chapter 3 line 136 as the target on the basis of the local mention. The AI never enumerated each chapter's argumentative job, never compared candidate chapters, never asked "what argument-type is source-criticism, and which chapter is for that argument-type."

## Impact

- PR #112 misrouted; closed before merge after many turns of user correction.
- PR #111 already merged; audit pending against chapter 5's actual content. If misplaced, follow-up PR migrating the Egyptian-transformation-theology subsection.
- Approximately 1000 additional research findings queued for integration. Each integration is a misplacement risk at the AI's current chapter-selection error rate. Cost compounds with scale.
- The architectural division of labor across chapters is a fundamental property of the book the user expected the AI to internalize from chapter titles and the chapter-1 introduction alone.

## Root Cause

`CLAUDE.md` "Core Workflow for Adding Content to Chapters" codifies topic-adjacency as the chapter-selection algorithm. Step 1 instructs: *"Read full chapter + grep for keywords → Find where topic already exists."* Step 2: *"If exists: plan to ENHANCE that section. If not: verify by searching synonyms."* The workflow's only chapter-selection logic is "where the topic already has a local hook." An AI following the workflow correctly cannot help but choose chapters by topic-adjacency, because the workflow tells it to.

The workflow's implicit Step 0 — *choose the right chapter* — is unspecified. The choice is left to the AI's judgment, which the workflow shapes toward topic-adjacency. There is no tracked statement of each chapter's argumentative job, no required comparison across chapters before placement, no wrapper enforcement at the chapter-selection step. The book's architectural division of labor exists only in the user's head.

PM-0005 added "read the file before editing" enforcement. PM-0005 does not catch chapter-selection errors; it catches workflow-bypass. The PM-0005 planned `chapter_anchors_referenced` schema field requires anchors from the chosen chapter; it does not test whether the chosen chapter is correct, only that anchors within it can be quoted.

Adding text-rules to MEMORY.md or CLAUDE.md does not fix this. PM-0005 already established that text rules don't enforce — only structural mechanisms do.

## Action Items

- [x] [mitigate-this-incident] Close PR #112. The chapter 3 paragraph is misplaced; source-criticism of the Lazarus parable belongs in chapter 5 (Gospels-to-cities geographic mapping), not chapter 3 (title-theology).

- [ ] [mitigate-this-incident] Audit PR #111 (merged) against chapter 5's actual content once chapter 5 has been read in full; if misplaced, follow-up PR migrating the Egyptian-transformation-theology subsection to its correct home. (#113)

- [ ] [prevent] Author `docs/book_structure.md` (tracked, in-repo) as part of this PR. For each chapter, state in verifiable form: (a) the argumentative job in one sentence; (b) misleading topical hooks that draw the AI to the wrong chapter (e.g., *"the Lazarus parable is mentioned in ch3 as anthropology evidence; source-criticism of the parable belongs in ch5, not ch3"*) — load-bearing, names topic-adjacency traps explicitly so the AI must check against them; (c) cross-references for misplaced topics (*"Gospels-to-cities geographic mapping → ch5"*). The AI authors this file by reading every chapter in full and submits for user correction; the user is the source of truth on each chapter's job, but producing the artifact is the AI's responsibility. (#114)

- [ ] [prevent] Rewrite "Core Workflow for Adding Content to Chapters" in `CLAUDE.md`. Replace the current Step 1 (*"Read full chapter + grep for keywords → Find where topic already exists"*) with an architecture-first sequence: (i) read `docs/book_structure.md`; (ii) for each chapter, write a one-sentence relationship between the proposed material and that chapter's argumentative job; (iii) only after that book-level comparison, identify the target chapter and search for a local hook within it. The current Step 1 is the topic-adjacency rule codified as process; rewriting removes the codification. (https://github.com/mvdatacenter/claude-instructions/issues/141)

- [ ] [prevent] Extend `.pr-review.json` schema (and `gh-wrapper.sh` validation) for `chapter*.tex` edits to require a `placement_justification` field with three components: (i) the target chapter, named; (ii) for each other chapter in the book, one sentence on why the material does not belong there (the comparison is mandatory; mentioning only the target fails validation); (iii) a verbatim quote of the target chapter's argumentative job from `docs/book_structure.md`. The wrapper validates: every chapter in the book is enumerated by number, the target's job-quote matches `book_structure.md`, no chapter is skipped. (https://github.com/mvdatacenter/claude-instructions/issues/142)

- [ ] [prevent] Update PM-0005's planned PreToolUse hook to also require `docs/book_structure.md` has been Read in the current session before any chapter edit. The "did you read" hook expands from "did you read the chapter" to "did you read the chapter AND the book-structure file." (https://github.com/mvdatacenter/claude-instructions/issues/143)

- [ ] [detect] Add scenario `chapter-misplacement-via-topic-adjacency.md` to `claude-instructions/scenarios/`. Setup: manuscript repo with multi-chapter scope and a topic with misleading local hooks in the wrong chapter. Prompt: AI asked to add material on the topic. Eval: AI's `.pr-review.json` `placement_justification` must enumerate all chapters and reject the topic-adjacent-but-misplaced one explicitly. Anti-pattern: AI grabs the local hook and edits the wrong chapter. (https://github.com/mvdatacenter/claude-instructions/issues/144)
