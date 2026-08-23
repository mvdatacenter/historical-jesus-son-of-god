# PM-0008: A Generated-Files Declaration Is Enforced By A Check, Not Its Own Wording

## What Happened

Commit `a97d58e` added a `.gitattributes` rule marking the translated editions `linguist-generated`, under the message "declare translations/ generated so it is regenerated, not hand-edited". The two commits that followed it on the same branch hand-edited those files.

```evidence
$ git log --oneline --format="%h %s" a97d58e~1..0ff3fab
0ff3fab docs: state the translations guidance in the affirmative (#175)
aa50c4c fix: move the last five Polish attributions into citations and drop the sweep's exemption (#175)
46a64bb fix: give the Polish edition a bibliography and hold translations to the citation invariants (#175)
a97d58e fix: declare translations/ generated so it is regenerated, not hand-edited (#175)

$ git show --format= --name-only a97d58e
.gitattributes
$ git show --format= --name-only 46a64bb
.gitattributes
.github/workflows/tests.yml
README.md
docs/REVIEW.md
scripts/test_source_registry.py
translations/README.md
translations/polish/chapter1_po.tex
translations/polish/chapter4_po.tex
translations/polish/chapter5_po.tex
translations/polish/manuscript_po.tex
$ git show --format= --name-only aa50c4c
scripts/test_source_registry.py
translations/README.md
translations/polish/chapter4_po.tex
translations/polish/chapter5_po.tex
```

The edits moved twenty-one scholar attributions out of Polish prose and into `\cite{}` commands. They were made to clear this repository's own review gate, which had blocked the branch on the Modern Scholars rule of `docs/REVIEW.md` after the same branch extended that rule to read `translations/*/*.tex`. Editing the Polish cleared the block. At `translations/polish/chapter4_po.tex` two names with no bibliography entry to receive them, Eldon Epp and Michael Bird, were deleted rather than moved; the author recorded at the time that this arguably needed the operator's prior agreement, and made the edit without obtaining it.

Three of the twenty-one lines now state something the English does not. At `translations/polish/chapter5_po.tex:268` the Polish credits "trzy niezależne opracowania" — three independent studies — where `chapter5.tex:334` gives no count and instead lists four civic behaviours the Polish drops. At `translations/polish/chapter5_po.tex:962` the single sentence of `chapter5.tex:1485` becomes five Polish sentences. At `translations/polish/chapter4_po.tex:504` the "over 250 transcriptions and manuscripts" of `chapter4.tex:517` is gone. A rerun of `scripts/translate_book.py` discards all twenty-one lines. The branch reached `main` as `bc53cbb`.
