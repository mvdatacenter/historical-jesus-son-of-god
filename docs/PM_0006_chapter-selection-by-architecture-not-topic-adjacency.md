# PM-0006: Chapter Selection by Architecture, Not Topic-Adjacency

## What Happened

Two recent PRs placed manuscript content in the wrong chapter (PR #111 merged, PR #112 closed). Both placements were architecturally obvious mistakes — recognizable on a glance to anyone who knows each chapter's argumentative job. Neither was off-the-cuff. The AI executed the prescribed chapter-selection step at full thoroughness — *read full chapter + grep keywords → find where topic already exists* — and the thoroughness produced confidence in the wrong answer. The prescribed step, run correctly, fails at its main task.

## Root Cause

Step 1 of `README.md` "Core Workflow for Adding Content to Chapters" reads as *read full chapter + grep keywords → find where topic already exists*. The step reads the chapter that already has a local mention of the topic and treats finding the mention as the placement decision. The scope of the step is one chapter; comparing the candidate against other plausible chapters is outside the step. PR #111 and PR #112 each read the chosen chapter in full, found a local hook, and committed there — fully compliant with the step as written. Correct placement requires reading every plausible candidate chapter in full and each candidate's Q&A file in full, then picking from the comparison of actual chapter content.

## Action Items

- [x] [prevent] Update Step 1 of `README.md` "Core Workflow for Adding Content to Chapters" so that selection happens by reading every plausible candidate chapter in full and reading each candidate's Q&A file in full, picking the target chapter from this comparison of actual content. Done in this PR.
- [x] [prevent] Update Step 6 of the same workflow so that pre-commit verification happens by re-reading the target chapter in full and re-reading the chapter's Q&A file in full. Done in this PR.
