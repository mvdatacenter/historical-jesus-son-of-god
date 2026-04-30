# Review Guidelines

Repo-specific review checklist for manuscript changes.

## No Modern Scholar Name-Dropping

Modern scholar names must never appear in manuscript text.
Ideas stand on their own; cite works via `\cite{}` only.

Ancient authors (Josephus, Eusebius, Philo, Jerome, Justin Martyr, Clement of Alexandria, etc.) are primary sources and ARE named in text.

**Exception — eponymous academic standards:** When a modern scholar's name IS the standard name of a test, scale, law, or method (e.g., "Rank--Raglan scale," "Bechdel test," "Richter scale"), the name is allowed. These function like "Newton's law" — the name identifies the tool, not the scholar's authority. The test is: could you remove the name without the reader losing the ability to look up the concept? If not, it's an eponymous standard, not a name-drop.

**Check:** `grep -n` for modern scholar surnames in `chapter*.tex`. Any match outside a `\cite{}` command is a violation unless it names an eponymous academic standard.

**Anglophone bias warning:** AI models systematically catch English-language scholar names (MacDonald, Walsh, Whitmarsh) while missing non-English names (Schrader Polczer, de Boer, van Kooten, Tal Ilan, Young-Ho Park). Do NOT rely on "feels like a name-drop" — grep mechanically for all names appearing before `\cite{}` or with attribution verbs (argues, notes, shows, demonstrates, identifies, proposes, concludes).

## Alexandria Pipeline is Internal Research Data

The Alexandria extraction pipeline (`alexandria-pipelines` repo) is an internal research tool.
References to specific data sources (e.g., "YouTube") must not appear in documentation, guidelines, or manuscript text.
Findings from the pipeline are treated as research leads that enter the standard three-gate pipeline (ChatGPT drafting, Claude review, citation verification).

## Evidence Anchoring

Every factual claim in the manuscript must be anchored to a specific primary source, inscription, or archaeological datum.
Consensus laundering ("most scholars agree," "it is generally accepted") is forbidden without naming who, where, and when.

## Claims Must Carry Their Own Argument

Removing a scholar's name is not enough. A bare claim with only a `\cite{}` is not an argument — it is a dressed-up name-drop.

If a claim is not widely accepted, the text must present the evidence that supports it. The reader needs to see *why* the claim holds, not just *that* someone said it.

**Bad:** "The evangelists composed their narratives through deliberate mimesis of Greek models `\cite{macdonald:mimesis}`."
— This states a conclusion without evidence. The reader has no reason to believe it.

**Good:** "The number of proper names in Luke's Gospel that map to characters in the Odyssey, combined with shared narrative structures such as the storm at sea, the hospitality scenes, and the recognition motif, indicates deliberate literary mimesis rather than coincidence."
— This presents the observable data that supports the claim.

**Rule:** When integrating an Alexandria finding or any external research, extract the *evidence* — the specific data points, textual parallels, archaeological facts — not just the conclusion. If the finding only provides a conclusion without supporting data, either:
1. Research the supporting evidence (download the work, ask ChatGPT for specifics, query Alexandria for more detail), or
2. Do not add it to the manuscript until evidence is available.

## Foreign Language Formatting

All foreign words must follow the project's language rules (see README.md "Greek, Hebrew, and Other Languages"):

- **First mention:** Transliteration with original script in parentheses — `\emph{homoousios} (ὁμοούσιος)`
- **Subsequent mentions:** Original script only — `ὁμοούσιος`
- **Longer fragments:** Original script first, then English translation — `τὸ πορφυροῦν αἷμα, "the purple of blood"`

**Common violations to catch:**
- Bare transliterations without original script on first mention
- Original script dumped without transliteration on first mention
- Missing `\emph{}` on transliterated words
- Foreign terms introduced without any formatting at all (e.g., plain "homoousios" instead of `\emph{homoousios} (ὁμοούσιος)`)

**Check:** Search new text for Greek/Hebrew/Latin terms and verify each follows the formatting convention.

## Writing Standards Checklist

This is a book. Write like a high-class author. Obey the basic rules of good writing: text must flow, paragraphs must connect, nothing is repeated, no unnecessary conclusions, no filler, no seams visible to the reader. Read what you wrote in context before committing. If it reads like AI output pasted into a chapter, rewrite it until it doesn't.

When the review finds a concern — weak logic, irrelevant information, bad placement — do not silently fix it or pass it. Send the concern back to ChatGPT with the specific problem and the surrounding chapter context, and work on a better version. ChatGPT may not have the full scope of the book in its memory, so include enough context for it to understand what the paragraph needs to do and where it sits in the argument.

Before accepting any new or rewritten text, check for:

### Logic

- **Logical coherence** — Can this sentence be written in simpler, clearer logic without losing any meaning? If yes, propose a simpler version to ChatGPT. AI slop survives by sounding complex. It never survives simplification.
- **Logical completeness** — Every "therefore," "thus," "this means," "this confirms" must be traced back. What specific sentence does it follow from? If you cannot point to the sentence, the connector is false. "The inscription confirms accuracy... therefore the accusation is civic" fails because accuracy and civic nature are different claims — one does not produce the other. Read the paragraph as a chain: does each sentence follow from the one before it, or does the text jump between unrelated points connected by false connectors? A logic problem sent as a style request to ChatGPT produces polished nonsense.

### Content

- **AI garbage** — Three tests, all must pass. First: does removing this sentence reduce factual content? If no, delete it. Second: does the reader need this information HERE to follow the argument? A sentence can contain true information and still be garbage if the reader doesn't need it at this point. "Thessalonica was founded by Cassander" is true but useless if the argument is about civic authority, not city founding dates. Third: would this information be more valuable in an earlier section as background? If yes, move it there or cut it — don't bury important context in the wrong place.
- **Distribution of findings** — Do not dump all findings into one paragraph at one insertion point. Each finding belongs where it is most relevant in the book. Background facts (like "Rome governed through Greek institutions") may belong in chapter 2 or 3 where ecclesia is first described, not in chapter 5 where it's buried. When ChatGPT returns multiple findings, distribute each to its natural location across the book.
- **Evidence anchoring** — Read each new factual sentence in the diff. Does it name a specific source (manuscript, ancient author + work, inscription, verse)? "The oldest manuscripts" is not anchored. "Codex Vaticanus and Codex Sinaiticus" is. If unverified through the citation pipeline, the claim does not get committed as final text.
- **GPT default framing** — Does the new text treat "Jewish" as the default category? Does it frame Egyptian/Greek elements as additions to a Jewish base? If yes, the framing contradicts the book's thesis. See "GPT Default Framing" section.

### Style

The Writing Style Rules in README.md apply to all text: direct ("this is X" not "this can be understood as X"), confident, evidence-first, simple language. One sentence per line is formatting only — sentences should be normal scholarly length.

- **Name-dropping** — Any modern scholar named in running text? Remove; keep `\cite{}`.
- **Consensus laundering** — Vague appeals to authority without specifics? Rewrite with evidence.
- **Clause stacking** — Multiple dependent clauses where one declarative sentence suffices? Simplify.
- **Audience simulation** — "This shows that..." / "It is important to note..."? Delete.
- **Jargon decoration** — Replace words that sound technical but do not add specific meaning with plain language. Test: if swapping the term for a simple word (like "real," "active," "working," "formal steps") keeps the meaning unchanged, replace it; if the term adds a precise distinction you would lose, keep it. Read the sentence aloud: if it sounds like a lecture instead of a clear explanation to a smart friend, simplify the wording without removing the idea.

### Context

- **Read the chapter after editing.** Read 20 lines before and after the insertion point. Does the new text match the argument being made? If the surrounding text argues X, the new text cannot assume not-X. Does each paragraph connect to the next? Is there a conclusion where there shouldn't be one? Does the new text repeat what the chapter already said? Would a reader notice where the insertion starts and ends?

## No Presupposed Outcomes

This is a research project that follows scientific and historical method. You do not get to invent results before running the experiment. A historian does not write "~50-70% of sources confirm the hypothesis" before reading the sources. A scientist does not fill in the results column before collecting data. The same standard applies to everything we produce — manuscript claims, pipeline designs, validation criteria, cost estimates.

Arbitrary numbers, percentages, thresholds, and success criteria are all forms of the same mistake. They give false confidence, anchor evaluation to made-up baselines, and create goals that have no relationship to reality.

**Bad:** "Step 1 reduces the set by ~50-70%." — Invented to make the table look complete.
**Bad:** "Success criteria: at least 40% filtered out." — Arbitrary threshold with no basis.

**Good:** Describe the mechanism. Define success in terms of quality ("verdicts have specific justifications"), not quantity. Let actual results supply the numbers.

**Rule:** If a number or threshold did not come from a measurement, a calculation, or a cited source, it must be removed. "I don't know yet" is always better than a fabricated target.

## GPT Default Framing

ChatGPT's training data overrepresents one strand of modern scholarship that treats everything in the biblical tradition as Jewish in origin, Christianity as emerging from Judaism, and Greek/Egyptian/institutional foundations as secondary influences requiring special justification. This default is not representative of the full range of Christian tradition, historical evidence, or global scholarship.

This is the exact position the book argues against. The book argues John is a Greek text, early Christianity has Greek institutional foundations, and the dominant modern scholarly consensus reflects narrow assumptions, not the weight of historical evidence.

**The mistake:** ChatGPT produces text that starts from the mainstream scholarly frame and tries to "add" Egyptian or Greek elements to it. The result reads as if the Egyptian/Greek argument is a minority opinion being cautiously proposed against an established Jewish baseline. This is backwards — the evidence presented in the chapter IS the baseline. The mainstream frame is what needs defending, not the book's argument.

**Example:** The chapter spends 30 lines proving John's theology matches Egyptian structures (Amun/Ra, creation-by-word, Memphite Theology, descent-ascent, judgment, eternal life). ChatGPT then drafts a follow-up paragraph that calls the same Wisdom texts "Jewish" and argues they are an "Egyptian-Jewish hybrid." This walks back the chapter's own argument by reimporting the mainstream frame the chapter just dismantled.

**Check:** When reviewing ChatGPT output, ask: does this text accept the mainstream US Protestant scholarly consensus as its starting point? Does it treat "Jewish" as the default category for anything in the biblical canon? Does it frame Egyptian/Greek origins as needing extra justification? Phrases like "Egyptian-Jewish hybrid," "Jewish Wisdom tradition with Egyptian influence," or "bridge between Jewish and Egyptian thought" are markers of this default.

**Rule:** Claude must catch this and push back on ChatGPT BEFORE presenting the draft to the user. If ChatGPT returns text with mainstream-default framing, Claude sends it back with a correction prompt explaining the book's thesis and the specific chapter context. The user should never see a draft that contradicts the book's argument — that is Claude's job to filter.

**Equal terminology for all traditions.** Do not use different registers for Jerusalem and Alexandria. If Jerusalem has "religion," Alexandria has "religion" — not "intellectual environment" or "philosophical tradition." If Jerusalem has "theology," Alexandria has "theology." Using softer or more academic language for Alexandria (e.g., "intellectual milieu," "philosophical system") while calling Jerusalem's output "religion" or "theology" implicitly downgrades Alexandria to a secondary, merely academic phenomenon. They are the same kind of thing: religion. Use the same words.

**Inform the reader, not just the scholar.** The target reader is an educated general reader, not a specialist. When the text builds on established scholarly findings, it must tell the reader those findings exist. Do not assume the reader already knows what scholars have found. If we argue "X is actually Egyptian," the reader first needs to know X exists and what has been said about it. A paragraph that refutes a scholarly position the reader has never heard of is incoherent. The rule: establish the known finding, then make the move.

**New text must be consistent with surrounding chapter context.** Read 20 lines before and after the insertion point. If the surrounding text argues X, the new text cannot assume not-X.

## Universal Tropes Are Not Evidence

- **Every cross-cultural parallel in manuscript text names a specific anchor.** The anchor is either an anomaly-demanding-explanation (a textual feature that is incoherent or unexplained on the standard reading and that the proposed parallel makes coherent) or a rare specific detail in combination (a multi-element structural pattern that is genre-specific). Example of the first: *Noli me tangere* (John 20:17) is incoherent in Pharisaic resurrection theology, which has no transitional-vulnerability concept; Egyptian transition-window theology (BD Spells 23, 89) supplies the framework that makes the line coherent. Example of the second: *call dead by name* → *dead emerges bound* → *unbinding command* is a three-step sequence shared with PGM necromancy, Apuleius's Zatchlas, Lucian's Hyperborean, and the Egyptian opening-of-the-mouth ritual. The combination is genre-specific even though no single step is unique.
- **Universal physical activity, universal literary trope, and shared theme without shared form do not function as anchors.** Mourning, washing, processions, and communal meals are naturally-emergent universal behaviour. Recognition-at-the-end, mistaken-identity-then-recognition, search-and-find, and separated-then-reunited are universal literary tropes. "Both texts are *about* resurrection" or *about* divine self-revelation is shared theme without shared form. Shared use of any of these is the null hypothesis, not evidence of cultural connection.
- **Transmitted custom and transmitted doctrine pass even when the substrate is naturally universal.** *Anointing as royal proclamation* is a specific ancient Near Eastern / Mediterranean tradition, not naturally-emergent behaviour. *Breath as the vehicle of an immortal soul* is a specific theological doctrine; every culture associates breath with vitality as a natural symbol, but breath-as-carrier-of-deathless-soul-or-indwelling-divine-presence is transmitted, not natural. Substrate (eating, breathing, mourning) can be naturally universal while the doctrine layered onto it (Eucharist, Holy Spirit transmission, specific funerary theology) is transmitted. The rule rejects naturally-emergent behaviour and natural symbolic association, not transmitted custom or transmitted doctrine.
- **The rule applies even within an already-established cultural context.** If the book has independently established that a Gospel comes from a specific milieu (through papyrology, manuscript distribution, philological evidence, etc.), a per-scene parallel that reduces to a universal trope still does not function as evidence for that milieu --- it reduces to decoration. Universal tropes do not become specific because the surrounding argument is specific.
- **An anchor to a primary source is necessary but not sufficient.** The anchor must be specific-by-form, not just specific-by-citation. A primary source that establishes only a shared trope is decoration with a footnote. This rule sharpens *Evidence Anchoring*: anchoring to a primary source is necessary, but the anchor must also be specific-by-form.
- **A parallel that reduces to a shared universal trope or shared topical theme is logged to Q&A and not presented as evidence.** For every cross-cultural parallel claimed in new manuscript text, name the specific anchor --- which anomaly is being explained, or which rare combination of details is being matched. If the parallel reduces to a shared universal trope or shared topical theme, log it to Q&A and do not present it as evidence.

## Temporal Relevance of Sources

Sources must be from the correct historical period. Citing a 7th century BCE amulet to explain a 1st century CE Antiochene text is not evidence unless the chain of transmission across those 700 years is demonstrated. Some traditions do carry across centuries — the Bill of Rights traces to Magna Carta, Egyptian funerary theology spans millennia with documented continuity. The question is not "is the source old?" but "is the continuity shown or assumed?"

Each gospel has a specific time and place. When citing a source from a different period as a parallel, the text must either show intermediate evidence of transmission or explicitly state that continuity is assumed and why.

**Do not apply opposite standards to the same problem.** A 700-year-old source is not automatically invalid and a 100-year-old source is not automatically a "gap." Both require the same treatment: state the source, state its date, argue the connection explicitly. If a distant source is relevant, explain why the pattern persisted. If a close source matches, use it without hedging. Do not dismiss sources from distant periods without argument, and do not apologize for sources that are obviously close in time and place. The book makes arguments — it does not present evidence and say "you decide."

Religious grammar, ritual structure, and regional practices often survive centuries of political upheaval. Political boundaries change; cult practice is more persistent. A 7th century BCE Syrian protective text may genuinely reflect patterns that survived into the 1st century — but that continuity must be argued, not assumed. A 2nd century CE author describing Syrian practices is straightforward evidence for the region's religious culture — no apology or hedging needed.

**Check:** For every non-biblical source cited as a parallel, verify: is the date stated? Is the relationship to the target text argued or just assumed? ChatGPT systematically cites the oldest and most famous texts in a tradition (Bronze Age Ugarit, Iron Age inscriptions) when period-appropriate sources exist. Catch this and demand the right period first — but do not then dismiss the older sources entirely without considering what may have persisted.

## Ch1 Spirit Rule

Chapter 1 is an overview of scholarly models. It surveys frameworks; it does not deep-dive into specific scholars' arguments.
Any addition to ch1 must match this register: one overview-appropriate sentence, not multi-sentence argument summaries.
