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

Before accepting any new or rewritten text, check for:

1. **AI garbage** — Does removing any sentence reduce factual content? If not, delete it.
2. **Name-dropping** — Any modern scholar named in running text? Remove; keep `\cite{}`.
3. **Consensus laundering** — Vague appeals to authority without specifics? Rewrite with evidence.
4. **Clause stacking** — Multiple dependent clauses where one declarative sentence suffices? Simplify.
5. **Audience simulation** — "This shows that..." / "It is important to note..."? Delete.
6. **Jargon decoration** — Academic vocabulary used for show rather than precision? Replace with simpler word.

## Ch1 Spirit Rule

Chapter 1 is an overview of scholarly models. It surveys frameworks; it does not deep-dive into specific scholars' arguments.
Any addition to ch1 must match this register: one overview-appropriate sentence, not multi-sentence argument summaries.
