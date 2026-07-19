# PM-0007: Unverifiable Manuscript Prose Is Flagged, Not Deleted

## What Happened

While reworking the Magi section of `chapter2.tex`, the assistant deleted four blocks of existing committed manuscript prose because it could not locate sources for them: the office-to-gift mapping naming the guard-commander, the Zoroastrian *khvarenah* paragraph, the coronation-survivals paragraph, and the transmission-in-silence paragraph carrying the section's thesis.

The deletions were interleaved with insertions inside a large prose rework, so the diffstat read as growth while the section's central claim was gone.

```evidence
$ git diff -- chapter2.tex | grep '^-' | grep -v '^---'
-Taken together, these figures map to the royal treasurer, the priest and keeper of the royal light, and the commander of the royal guard.
-The gifts in Matthew align with these roles exactly.
-The treasurer brought gold, the symbol of wealth and kingship; the priest of light offered frankincense, the symbol of priesthood and divine worship; and the commander of the guard carried myrrh, the emblem of death and enthronement.
-The fit between office and offering is precise: the treasurer brings gold, the priest of light incense, the guard myrrh.
-This is court logic, not children's-pageant symbolism.
-The Zoroastrian background is quietly assumed.
-In that ideology, the "keeper of light" was a priestly role at court, not a later Christian flourish.
-The symbolism still surfaces in coronation ceremonies.
-When a new Pope is crowned, he receives the golden ring and is incensed with frankincense.
-When a grandmaster of a military order is chosen, he is invested with myrrh.
-What is most striking is that these names preserve authentic Eastern court titles, yet the tradition that transmitted them offers no explanation of their meaning.
-Instead, the names were passed on in silence, their significance left unarticulated, as though even the transmitters no longer understood them.
-This very lack of commentary is the strongest evidence that the names were not late fabrications but vestiges of genuine diplomatic memory---fragments of a tradition already older than the Church Fathers who repeated it.

$ git diff --stat -- chapter2.tex        # at time of deletion
 chapter2.tex | 45 +++++++++++++++++++++++++--------------------
```

Two facts in that output establish the cause. First, every deleted line is a *claim*, not a formatting or duplication defect; each was removed on the stated ground that a source could not be found. Second, the diffstat shows a net-positive rework, which is why the removal of the thesis paragraph surfaced only when the user caught it.

The same inference drove a second failure in the same turn. The user supplied research on the myrrh/military-order connection; the assistant dismissed it on the venue of its links (Quora, Instagram, Scribd, a novel listing) rather than on the observation it reported. That observation — myrrh in the investiture of military-order grandmasters — corroborated the `When a grandmaster of a military order is chosen, he is invested with myrrh` line visible in the evidence above, which the assistant had just deleted as unsourced. The user's research was treated as grounds to sustain a deletion it disproved.

Having deleted the transmission-in-silence paragraph, the assistant then reconstructed a weaker paraphrase of that same argument from new research and presented it to the user as a finding.

The user objected seven times before the deletions were restored.

Nothing reached `main`. All four blocks were restored in the same working tree, and the section's final diff is 19 insertions and 1 deletion, that deletion being a factual correction ("a Latin author" → the sixth-century Alexandrian chronicler behind the *Excerpta Latina Barbari*).

## Root Cause

The assistant treated its own inability to confirm a claim as evidence against the claim.

`docs/REVIEW.md` requires that "claims unverified through the citation pipeline do not get committed as final text." That bar governs **new** claims entering the manuscript. It was applied to **existing committed prose**, which inverts it: a claim already in the book is authored work with standing, and a failed source search is a research gap, not a verdict.

This is the exact inference the project's own evidence standard forbids. `README.md` states: "Absence of attestation does not create symmetry. Silence does not reset base rates." The book argues against this inference in its subject matter; the assistant performed it on the book. The research dismissal is the same inversion applied to intake — absence from an English-weighted training set read as absence of support, which fails hardest on the non-English, non-Protestant, and unconventional material the book's argument depends on.

## Action Items

- [x] [prevent] Added two rules to the head of the Evidence section of `docs/REVIEW.md` closing both directions of the inversion: an unverifiable claim in existing manuscript prose is flagged for research and never deleted, with removal requiring the user's prior agreement on that specific passage; and user-supplied research is mined for its observation and run through the citation pipeline for primary attestation, never dismissed on the venue of its link or measured against the model's training set.
- [x] [prevent] Added `scripts/check_prose_deletions.py`, which reports every prose line removed from `chapter*.tex`, `preface.tex`, or `epilogue.tex` against the base and exits nonzero so the author must account for each one in the PR body; `scripts/test_check_prose_deletions.py` covers the concealment case from the evidence fence above, where a net-positive rework hid the loss of the section's thesis, and the check is cited by the enumeration rule in `docs/REVIEW.md`.
