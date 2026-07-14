# Review Guidelines

Repo-specific review checklist for manuscript changes. Rules are enforced rule-by-rule via `.pr-review.json`.

## Repository Boundary

- **Keep exploratory research outside the public repo.** This public repo contains manuscript text, citations and bibliography, source-verification material, and code or data directly used to construct public results. Exploratory work stays outside this repository because public readers need finished arguments and reproducible support rather than working notes or cache output. Move it here only after it becomes manuscript prose, verified citation or bibliography data, source-verification material, or result-building code/data.

## Modern Scholars

- **Modern scholar names do not appear in manuscript text outside `\cite{}`.** Ideas stand on their own; reference works via `\cite{}` only. Ancient authors (Josephus, Eusebius, Philo, Jerome, Justin Martyr, Clement of Alexandria, and so on) are primary sources and are named in text. The exception is eponymous academic standards (e.g., "Rank-Raglan scale," "Bechdel test," "Richter scale") — the name identifies the tool rather than the scholar's authority; test by whether removing the name leaves the reader unable to look up the concept.
- **A claim with only a `\cite{}` is not an argument; the text presents the evidence.** Removing the scholar's name is not enough. If a claim is not widely accepted, the text shows the specific data — proper names mapping to Odyssey characters, shared narrative structures, archaeological facts — that supports it.
- **Reviewers grep `chapter*.tex` mechanically for surnames, including non-English ones.** AI systematically catches English-language names (MacDonald, Walsh, Whitmarsh) and misses non-English ones (Schrader Polczer, de Boer, van Kooten, Tal Ilan, Young-Ho Park). Grep for all names appearing before `\cite{}` or with attribution verbs (argues, notes, shows, demonstrates, identifies, proposes, concludes). A match outside `\cite{}` is a violation unless it names an eponymous standard.

## Evidence

- **Every factual claim cites a specific source on the line that makes the claim.** Manuscript, ancient author + work, inscription, verse, archaeological datum — name it. "The oldest manuscripts" is not anchored; "Codex Vaticanus and Codex Sinaiticus" is. Vague appeals to authority ("most scholars agree," "it is generally accepted," "the consensus view") are rewritten with the specific who, where, and when. For sources from a different period than the target text, state the date and argue transmission or persistence — both 700-year-old and 100-year-old sources require the same treatment. Cult practice, ritual structure, and regional religious grammar persist through political upheaval — a 2nd-century CE source on Syrian religion is straightforward evidence for the region's earlier cult unless a specific rupture is shown. ChatGPT systematically reaches for the oldest and most famous texts when period-appropriate sources exist; catch this and demand the right period first. Claims unverified through the citation pipeline do not get committed as final text.
- **Modern source labels stay in citations; clear source names stay in prose.** Bible verse numbers are acceptable because readers expect that convention, and manuscript shelfmarks may be necessary when identifying a witness. Modern editorial unit labels for ancient corpora, such as `Spell 17`, usually move to the citation while the prose keeps the source name and the concrete evidence. If the text says `Book of the Dead`, a revision keeps `Book of the Dead` in the sentence. Compact quotations such as "I know the name of that god" stay when they are accurate and relevant.

## Foreign Language Formatting

- **First mention of a foreign term gives transliteration with original script in parentheses.** Example: `\emph{homoousios} (ὁμοούσιος)`.
- **Subsequent mentions use original script only.** Example: `ὁμοούσιος`.
- **Longer fragments give original script first, then English translation.** Example: `τὸ πορφυροῦν αἷμα, "the purple of blood"`.
- **Reviewers grep `chapter*.tex` for common formatting violations.** Catch: bare transliteration without original script on first mention (e.g., plain `homoousios`), original script dumped without transliteration on first mention, transliterated words missing `\emph{}`, and second-mention text still re-stating the transliteration when original script alone is required.

## Logic

- **Each sentence is written in the simplest logic that preserves the meaning.** If a sentence can be rewritten more clearly without losing meaning, rewrite it. AI slop survives by sounding complex; it never survives simplification.
- **Every logical connector traces back to a specific prior sentence.** "Therefore," "thus," "this means," "this confirms" — each must follow from a named sentence. "The inscription confirms accuracy... therefore the accusation is civic" fails because accuracy and civic nature are different claims; one does not produce the other.

## Content

- **Each sentence adds factual content the reader needs at this point in the argument.** Three tests, all must pass: does removing the sentence reduce factual content; does the reader need this information here to follow the argument; would the information be more valuable earlier as background?
- **Each finding lives where it is most relevant in the book, not where it is convenient.** Background facts (like "Rome governed through Greek institutions") may belong in chapter 2 or 3 where ecclesia is first described, not in chapter 5 where they would be buried. When ChatGPT returns multiple findings, distribute each to its natural location across the book.

## Style

- **Clauses stack only when they each add distinct information.** Multiple dependent clauses where one declarative sentence suffices: simplify.
- **The text does not address the reader directly.** Phrases like "this shows that...," "it is important to note...," and "we can see" are removed; present data and let the reader draw the conclusion.
- **Use the clearest accurate wording.** A less common or more specialized word stays only when it adds meaning the ordinary word would lose. Reviewers compare the old and new sentence: if the revision replaces a clear word with a less common word that says the same thing, ask for the ordinary word. Examples: `use` instead of `utilize`; `title` for ordinary use and `epithet` when the technical term matters; `Book of the Dead` rather than a broader category label when the source name is the clearest wording.
- **A summarizing sentence earns its place by retrieval: most of what it gathers lives in other chapters or in cited works.** A sentence that enumerates items already present in the immediately preceding sentences restates what the reader just read and treats them as unable to hold one passage. Review check: for each summarizing sentence in the diff, locate every item it names; when the items sit in the same passage, delete the sentence.

## GPT Default Framing

ChatGPT defaults to one strand of modern scholarship that treats everything in the biblical tradition as Jewish in origin and Christianity as emerging from Judaism, with Greek and Egyptian elements as later influences requiring justification. This is the position the book argues against; the mainstream frame is what needs defending, not the book's argument.

- **New text does not treat "Jewish" as the default category.** Phrases like "Egyptian-Jewish hybrid," "Jewish Wisdom tradition with Egyptian influence," and "bridge between Jewish and Egyptian thought" reimport the mainstream frame the book just dismantled. Catch this and push back on ChatGPT before the draft reaches the user.
- **Equal terminology applies to all traditions.** If Jerusalem has "religion" or "theology," Alexandria has "religion" or "theology" — not "intellectual milieu" or "philosophical system." Softer or more academic language for non-Jerusalem traditions implicitly downgrades them.
- **Text builds on established findings only after the reader sees them.** A paragraph that refutes a scholarly position the reader has never heard of is incoherent. Establish the known finding, then make the move.
- **New text matches the surrounding chapter argument.** Read 20 lines before and after the insertion point. If the surrounding text argues X, the new text cannot assume not-X. Does each paragraph connect to the next? Does the new text repeat what the chapter already said? Would a reader notice where the insertion starts and ends?

## Method

- **Numbers, percentages, thresholds, and success criteria come from a measurement, calculation, or cited source.** "Step 1 reduces the set by ~50-70%" or "Success criteria: at least 40% filtered out" without a derivation are invented anchors. "I don't know yet" is better than a fabricated target.
- **Chapter 1 stays at survey register.** Give each scholarly model a brief account of its strongest evidence, using as many sentences as clarity requires.
