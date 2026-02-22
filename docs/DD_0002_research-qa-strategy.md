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

## Alexandria: Extended Research Materials

The `alexandria-pipelines` repo is the project's extended research corpus. It uses knowledge extraction pipelines to surface scholarly insights from unstructured sources that are not well-indexed by search engines or well-represented in LLM training data.

**Note:** This is a public repo. The specific data sources and extraction targets used by Alexandria are proprietary. Do not disclose them in public-facing documentation.

### Research Scope Expansion

The existing research process (ChatGPT + Claude + citation verification) covers published scholarship and primary sources. Alexandria extends this to a broader body of scholarly discourse that may not appear in print or standard databases.

The next phase of research should scan Alexandria's extracted materials for:

- Arguments or evidence relevant to the book's thesis that we haven't encountered yet
- Counter-arguments to claims already in the manuscript
- Scholarly debates or positions that challenge or support our framing
- Primary source references that we haven't tracked down

Any finding from Alexandria feeds into the same three-gate pipeline: ChatGPT drafting, Claude review, and citation verification before it reaches the manuscript.

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
