# PM-0008: Manuscript prose is composed as one argument, not appended lines

## What Happened

Between September 2025 and August 2026, manuscript prose entered this repository in an additive mode: each pull request drafted its sentences as standalone units, polished them as standalone units, and reviewed them as standalone units. The style guidance in force made the whole argument the unit — this repository's `docs/writing-standards.md` has the evidence carry the argument for the reader, and the prose rules these pull requests were reviewed under state that a passage is composed and reviewed as one argument, with every inherited sentence earning its place in it. Text produced additively reads well in isolation and fails in context: it contradicts its own citations, the lines above it, other chapters, or the corpus it describes, and it leaves the book's argument with holes where a load-bearing step is asserted but never shown. The operator named the mode while this record was in review:

```evidence
basically you are ignoring style guidelines and the argument flow and only keep revering to your own style and "adding lines of code" mode
```

The trigger. On 2026-08-20, pull request #173 (branch `feat/172-preserved-lyons-and-vienne-manuscript-branch-has`) added a paragraph to `chapter5.tex` to fill a hole of exactly this making — the summary prepared for the pull request concedes that the chapter had claimed a network while showing no instance of it:

```evidence
the chapter asserted that integration without ever showing it operate, so without this paragraph it claims a network and shows no single instance of one
```

Written additively, the patch for that hole opened a new context failure. The paragraph opens with a priority claim about the churches of Lyons and Vienne, and the same prepared summary describes it as supplying "the moment the West enters from the inside". The sentence states no scope — first attested where, among what candidates — and the paragraph's own citations contain the countercase: the same witnesses write to Eleutherus, bishop of Rome, an older Western church standing in the very evidence cited. Ten lines above it, the chapter already dates Carthage's church to c. 180, three years after the paragraph's 177.

```evidence
295:Gaul's earliest attested churches appear in Eusebius, who dates the persecution at Lyons and Vienne to the seventeenth year of Antoninus Verus---conventionally 177 AD \cite[Book 5, Introduction 1]{eusebius:he}---and names Gaul as its setting \cite[5.1.1]{eusebius:he}.
The same imprisoned witnesses sent further epistles to those churches and to Eleutherus at Rome \cite[5.3.4]{eusebius:he}.
The next Christian city to appear \emph{after} the New Testament's Greek world is Carthage, and it appears in the late second century (c.~180--200 AD, attested in the Scillitan Martyrs and Tertullian).
```

The paragraph passed every step of the process, and every step read it as standalone text. The citation pipeline returned LOCATED for all five citations — it verifies that each cited passage exists in the downloaded source, and it did exist; no step read any source for competing candidates, and no step read the paragraph against the chapter it entered. The review pass against `docs/REVIEW.md` passed it. CI passed it. The session that composed the paragraph reported the pull request verified and ready to merge. The rules in force at composition time — `docs/REVIEW.md` Evidence ("Every factual claim cites a specific source on the line that makes the claim") and the prose evidence rules that weigh every inference against the candidate pool it is drawn from — were in the composing session's hands, and the session wrote and approved an unscoped priority claim anyway. The reviewing pass was the same session, so the author reviewed the author.

The operator caught it on 2026-08-21 and stopped the work:

```evidence
You did not qualify the gaul churches were the first one in the western empire (outside of Rome). i dont know if they really were the only ones or if we have no plausible guesses on other parts of the empire
```

```evidence
the core idea of the book is to write cogent logical arguments, not arguments that immediately invite rightful criticism of covering up
```

The same day, on the operator's order, the manuscript was swept for the sharpest measurable sub-class of the additive mode: priority and uniqueness claims — "first", "earliest", "oldest", "only", "no other", "not one", "never", "none" — published without a scope statement and without a survey of the candidate pool the claim quantifies over. The sweep confirmed twenty instances: the PR #173 trigger plus nineteen in the merged manuscript, every one of which predates the trigger and entered through earlier pull requests: git blame at `origin/main` shows the last commit to touch each claim line belongs to one of twelve pull requests — #15, #16, #25, #26, #30, #33, #37, #42, #57, #60, #62, and #76 — all merged between September 2025 and February 2026, months before the trigger. Of the twenty: five are contradicted from the book's own pages or from sources already in this repository; three are contradicted by the corpus's own text at Acts 28:12–14; eight state a universal against a named standard countercase that has not been run through the citation pipeline; four state a universal over a pool the page never enumerates. Each contradicted instance fails at a measurable distance from its own context: the countercase sits in the claim's own citation set, ten lines above it, elsewhere in the same chapter, in another chapter of the same book, or in the corpus the claim quantifies over. A claim in the last two groups may yet survive its survey — what is recorded here is that it was published without one.

Contradicted from the book's own pages or this repository's sources:

- PR #173 trigger (branch, `chapter5.tex:295`) — "Gaul's earliest attested churches" framed as the West's entry; Eleutherus of Rome sits in its own citation set, and the chapter's Carthage paragraph sits ten lines above.
- `chapter5.tex:291` — "not one mentions any Western location at all", said of a list that opens with 1 Clement; 1 Clement chapter 5 has Paul reach "the extreme limit of the west". Verified in this repository's downloaded source text:

```evidence
228:, having taught righteousness  to the whole world, and come to the extreme limit of the west,  and suffered
```

- `chapter5.tex:317` — "where Greek civic assemblies existed, Christianity appears instantly in the first century"; the same chapter concedes at line 565 that Alexandria, the largest Greek city of them all, "appears only obliquely".
- `chapter5.tex:320` — "not one non-Greek city---Latin, Punic, or otherwise---shows a church until more than a century later"; Rome is a Latin city, and the chapter's own line 293 concedes "beyond Rome itself".
- `chapter5.tex:860-861` — the five named commentators "agree absolutely that there must be four and only four" gospels and "none of them even considers a fifth Gospel or a reduction to one or two"; the book's own `chapter1.tex:80` records Marcion using a single gospel.

Contradicted by the corpus's own text:

- `chapter5.tex:298` — "Massalia, the Greek cities of Sicily, the northern Black Sea colonies---do not appear at all"; Syracuse appears at Acts 28:12.
- `chapter5.tex:306` — a corpus "never once leaking into adjacent Greek-speaking nodes", probability "effectively zero" (a number with no calculation behind it); Acts 28:13–14 has brethren at Puteoli, the Greek-founded Dicaearchia in Campania.
- `chapter5.tex:310` — "None occur.", closing the list of diffusion predictions the two Acts passages answer.

Universal claims against a named standard countercase not yet run through the citation pipeline:

- `chapter5.tex:292` — "zero awareness of churches in Gaul, Spain, North Africa"; the 1 Clement passage above is read as Spain in the standard literature.
- `chapter5.tex:782` — "The eagle is the oldest continuous royal symbol of the eastern Mediterranean"; the Horus falcon is the royal symbol of Egypt millennia earlier.
- `chapter5.tex:924` — the earliest Oxyrhynchus manuscripts are "overwhelmingly Johannine"; Matthew papyri from Oxyrhynchus (P1, P77, P104) sit in the same pool, and no count is tabulated on the page.
- `chapter5.tex:929` — "No early Oxyrhynchus papyrus contains Mark or a fourfold gospel collection"; the same uncounted pool.
- `chapter5.tex:935` — "No parallel non-canonical corpus anchored in Egypt exists for Mark, Matthew, Luke, or Paul"; the Gospel of the Egyptians and the Egerton Gospel are Egypt-anchored non-canonical candidates.
- `chapter5.tex:131` — Stoic writers "never combine it with branding, sealing, thrones, officers, and assemblies"; the Roman cult pool holds the Mithraic soldier grade with its sealing rite.
- `chapter2.tex:989` — among the ossuary inscriptions "only one uses the construction ``brother of.''"; the published corpus literature reports a second.
- `chapter2.tex:1045` — "No other crucified person was buried in a tomb."; the Giv'at ha-Mivtar excavation found a crucified man in a rock-cut tomb.

Universal claims over a pool the page never enumerates:

- `chapter5.tex:134` — "This cluster has no parallel in philosophical moralism"; no survey of the pool appears.
- `chapter2.tex:403` — "not one of the many known Greek ecclesia gathered weekly on Sunday"; the "many known" are neither counted nor cited.
- `chapter1.tex:36` — spreading "at a pace no other apocalyptic sect achieved"; no comparison set appears.
- `chapter1.tex:41` — "crucifixion was never the fate of an apocalyptic preacher for prophesying"; the known pool (Theudas, the Egyptian, Jesus son of Ananias) is never enumerated.

The merged-manuscript lines, as they stand at `origin/main`:

```evidence
291:Numerous early Christian writings survive from the first half of the second century---1 Clement \cite{clement:firstclement} (c.~96 AD), Ignatius of Antioch \cite{ignatius:letters} (c.~110 AD), the Didache \cite{didache} (c.~80--120 AD), the Shepherd of Hermas \cite{shepherd:hermas} (c.~90--140 AD), Papias of Hierapolis (c.~120 AD), Quadratus (\emph{Apology}, c.~125 AD), Aristides (\emph{Apology}, c.~125--135 AD), Polycarp \cite{polycarp:philippians} (mid-second century), and Hegesippus (\emph{Hypomnemata}, c.~160--180 AD, who traveled the empire documenting Christian communities)---and not one mentions any Western location at all.
292:These authors actively list churches, send letters, and reference Christian communities across the eastern Mediterranean, yet they show zero awareness of churches in Gaul, Spain, North Africa, Germania, or Britain.
298:Greek-speaking cities outside that imperial lattice---Massalia, the Greek cities of Sicily, the northern Black Sea colonies---do not appear at all, despite sharing language, commerce, literacy, and maritime access.
306:The probability that a corpus containing hundreds of geographically explicit references would fully saturate one political-civic graph while never once leaking into adjacent Greek-speaking nodes is effectively zero.
310:None occur.
317:The pattern is definitive: where Greek civic assemblies existed, Christianity appears instantly in the first century.
320:And not one non-Greek city---Latin, Punic, or otherwise---shows a church until more than a century later.
565:The city appears only obliquely, as the origin of Apollos (Acts 18:24), who arrives already trained in the Scriptures and requiring only correction on baptism.
782:The eagle is the oldest continuous royal symbol of the eastern Mediterranean and the political face of the eastern quadrant of the ancient world.
860:The key observation is that all of these authors disagree on the details of which animal matches which book but agree absolutely that there must be four and only four.
861:Irenaeus, Victorinus, Augustine, Jerome, and Athanasius inherit different local traditions about animal-evangelist pairings, yet none of them even considers a fifth Gospel or a reduction to one or two; the fourfoldness is treated as cosmological, not editorial.
924:The earliest securely dated Christian manuscripts from Oxyrhynchus are overwhelmingly Johannine---not only the Gospel of John but also Johannine epistles and Johannine-associated non-canonical works---establishing Egypt's earliest scriptural profile as an entire Johannine literary ecosystem rather than a single gospel preference.
929:No early Oxyrhynchus papyrus contains Mark or a fourfold gospel collection; Luke appears only paired with John in P\textsuperscript{75}, not as an independent Egyptian tradition; Mark is similarly sparse and late across all Egyptian papyrological evidence.
935:No parallel non-canonical corpus anchored in Egypt exists for Mark, Matthew, Luke, or Paul: synoptic-associated apocrypha are unattested in Egyptian manuscripts, infancy gospels circulate trans-regionally without forming an Egyptian canon, and Pauline apocrypha show no localized Egyptian clustering.
```

```evidence
403:The one important exception: while some Greek ecclesia met a few times a month, not one of the many known Greek ecclesia gathered weekly on Sunday.
989:Among more than a thousand known ossuary inscriptions, only one uses the construction ``brother of.''
1045:No other crucified person was buried in a tomb.
36:Yet the same message proved astonishingly persuasive among Greeks, spreading across cities and cultures at a pace no other apocalyptic sect achieved.
41:And most telling, crucifixion was never the fate of an apocalyptic preacher for prophesying.
```

The additive mode recurred inside this record. The operator's order for it was general:

```evidence
look for many examples of this garbage argument making by AI in the what happened section
```

The first draft of this account answered with the priority-claims sub-class framed as the whole problem — an account complete as standalone text, with the general failure it sits inside unnamed. The operator corrected it while the account was in review:

```evidence
while you can keep this, again, i said i wanted a more general problem first. please expand your PM. we need to make sure the text as a whole simply makes good complete argument without a giant hole in the middle. this was another case of you writing text that is good as standalone but garbage when read in context.
```

No manuscript file was changed by this account. The affected passages stand as quoted, and repair is ordered to begin only after this record's action items are merged. Tracking: issue #176.
