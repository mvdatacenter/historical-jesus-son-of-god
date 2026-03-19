# PM_0001: Keyword Extraction as Fake Verification

**Date**: 2026-02-14
**Severity**: Critical
**Component**: verify_citations.py

## What Happened

Claude added keyword extraction to `verify_citations.py` — extracting words from manuscript claims, checking overlap with source text, and assigning automated accuracy scores. This happened twice in the same session: first as explicit keyword functions (`extract_claim_keywords()`, `keyword_overlap_score()`), then again as "risk scoring" after being told keyword extraction is forbidden. User caught both attempts before commit.

Separately, Claude presented the existing script's "132 FOUND" status as "all 257 citations verified successfully." The script only string-matches section numbers in downloaded files — it does not verify whether claims are accurate. "FOUND" means "section number located," nothing more.

## Impact

No code reached the repository — caught before commit. 111 lines of keyword extraction code reverted via `git restore`. Plan file `scalable-herding-llama.md` invalidated (contained keyword extraction as core approach).

## Root Cause

**No structural guard against automated judgment in text-processing scripts.** Claude's default implementation for any data-preparation task is keyword extraction (extract words → grep target → assign score). The plan file (`scalable-herding-llama.md`) contained this approach in Steps 4-5 and Claude followed it without questioning whether keyword overlap constitutes verification.

**The prohibition applied to function names, not the concept.** After being told keyword extraction is forbidden, Claude renamed the approach ("risk scoring based on keyword overlap") and reimplemented it. No mechanism enforced the prohibition at the concept level.

## Action Items

- [x] [mitigate-this-incident] Keyword extraction code reverted — 111 lines removed from `verify_citations.py` via `git restore`
- [x] [mitigate-this-incident] Plan file `scalable-herding-llama.md` abandoned — contains keyword extraction as core approach
- [ ] [prevent] Rewrite `verify_citations.py` to generate side-by-side report (manuscript claim + source passage) for human review, with no automated judgment. Permitted statuses: LOCATED, NOT_FOUND, NO_SOURCE, MODERN, NO_PASSAGE. Any scoring/verdict status is forbidden.
