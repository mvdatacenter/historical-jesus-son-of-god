# PM-0006: Chapter Selection by Architecture, Not Topic-Adjacency

## What Happened

Two recent PRs placed manuscript content in the wrong chapter (PR #111 merged, PR #112 closed). Both placements were architecturally obvious mistakes — recognizable on a glance to anyone who knows each chapter's argumentative job. The AI executed the prescribed chapter-selection step at full thoroughness — *read full chapter + grep keywords → find where topic already exists* — and the thoroughness produced confidence in the wrong answer.

## Root Cause

`README.md` carried a parallel "Core Workflow for Adding Content to Chapters" with its own enumerated steps, even though DD-0002 already specified the canonical pipeline (semantic chapter routing, model requirement, named anti-patterns including keyword extraction and topic-level matching). README is edited freely with no rule-by-rule review, so its workflow drifted: editorial judgment ("read every plausible chapter and pick by argumentative architecture") was reduced over successive edits to mechanical primitives ("grep for keywords"). DD-0002 names exactly this failure mode — "sub-frontier models silently degrade to topic-matching" — and a procedural step that prescribes grep produces the same degradation regardless of model quality. PR #111 and PR #112 followed the README workflow correctly; the workflow itself was the failure.

## Action Items

- [x] [prevent] Replace `README.md` "Core Workflow for Adding Content to Chapters" with a short chapter-edit boundary, removing the parallel enumerated workflow; implemented in #115 and updated when DD-0002 moved private in #131.
- [x] [prevent] Keep the README section scoped to new chapter content without re-enumerating routing steps; implemented in #115 and preserved after the public/private research split in #131.
