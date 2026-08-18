# Writing Standards

Read this before writing or reviewing any manuscript prose. When asking ChatGPT to draft manuscript text, paste this file into the prompt (see `docs/ai-governance.md`).

**FORMATTING NOTE:** One sentence per line. This governs formatting only. Keep sentences at normal scholarly length.

## Inline Citations: What's Allowed

**OK to cite inline (no footnote needed):**
- Bible verses: John 1:18, Mark 5:1-20, Acts 2:36
- Standardized papyrus numbers: 𝔓52, 𝔓66, P.Oxy. II 208
- Inscription corpora: CIS II 86, IGLS IV 1264, SEG 28.1235
- Ancient authors with work: Eusebius, Historia Ecclesiastica 3.39

**Everything else goes through `\cite{}` or becomes content:**
- Scholar name-drops like "Assmann (2001)", "Sterling (2023)", "Peters (2022)" look scholarly but convey nothing to the reader

**Rule:** If a scholarly work matters, convey the idea it establishes. Keep it as short as the idea allows, expanding when the idea needs more explanation or background. Every reference arrives with the content behind it.

**Example - Bad:** "as summarized by Assmann (2001)"
**Example - Good:** "Egyptian hymns describe Amun as hidden in name and essence"

The reader learns nothing from "Assmann (2001)" but learns the actual content from the second version.

## Modern Scholars: Ideas Stand on Their Own

Modern scholar names appear only inside `\cite{}`.
Ideas stand on their own.

Ancient authors (Josephus, Eusebius, Philo, Jerome, Justin Martyr, etc.) are primary sources and ARE named in text.

**Bad:** "MacDonald argues that the evangelists composed their narratives through deliberate mimesis."
**Also bad:** "The evangelists composed their narratives through deliberate mimesis of Greek models `\cite{macdonald:mimesis}`." — This is still a bare claim. Removing the name but keeping only a conclusion with a cite still leaves a bare claim.
**Good:** "The number of proper names in Luke that map to Odyssey characters, combined with shared narrative structures, indicates deliberate literary mimesis rather than coincidence." — The evidence carries the argument; the reader sees *why*.

**Bad:** "Walsh situates Paul within this educated Greco-Roman intellectual world."
**Good:** "Paul operated within an educated Greco-Roman intellectual world where pneuma functioned as substance rather than later metaphysical personification."

**Rule:** When a claim lacks wide acceptance, the text presents the evidence; the argument lives in the data, with `\cite{}` marking its source. Extract the data points together with the conclusion.

## AI Garbage: Formal Definition

AI garbage is prose that is grammatically correct and superficially fluent but adds no new information relative to its length.

A sentence or clause qualifies as AI garbage if it meets any of the following conditions:

1. **Restatement without informational gain** - The sentence repeats the same claim using synonyms, glosses, or paraphrase without adding evidence, scope, or constraint.
2. **Narrative inflation** - The sentence expands a simple factual statement into a historical vignette, ritual description, or imagined practice not supported by a source.
3. **Explanatory padding** - The sentence explains obvious implications that a competent reader can already infer.
4. **Consensus laundering** - The sentence invokes vague historical continuity, tradition, or widespread use ("for centuries," "commonly," "standard") without anchoring it to a specific context.
5. **Clause stacking** - Multiple dependent clauses are used where a single declarative sentence would fully convey the information.
6. **Audience simulation** - The sentence addresses an imagined reader ("this shows," "it is important to note," "we can see") instead of presenting data.

**Enforcement Rule:**
- Delete every sentence whose removal leaves the factual content unchanged.
- If a sentence can be reduced to one declarative clause without loss of information, it must be rewritten.
- AI garbage is removed or rewritten entirely.

**Example - Good:** "The triplet βασιλεία/δύναμις/δόξα appears in Hellenistic royal cult inscriptions."

**Example - Bad:** "The triplet βασιλεία/δύναμις/δόξα (kingdom/power/glory) is not Christian invention. It appears in Hellenistic royal cult inscriptions as standard acclamation language for Ptolemaic and Seleucid kings, and later for the Roman emperor in Greek provinces."

**Why it fails:**
- Adds glossing without need
- Inflates scope without evidence
- Stacks clauses without increasing precision

**Phrases that mark AI garbage (non-exhaustive):**
- "It is important to note..."
- "This shows that..."
- "Preserved in X and repeated for centuries..."
- "When [group] did X, they were..."
- "This is the quintessential..."

## Target Reader

**Target reader:** Educated general reader.
No theology degree required.
Comfortable with evidence, footnotes, and sustained argument.

## Jargon: When to Use vs. Replace

✅ **KEEP jargon when:**
- No simpler accurate word exists ("liturgical" - there's no replacement)
- Domain-standard term readers will encounter ("apocalyptically" - common in this field)

❌ **REPLACE jargon when:**
- It's just decoration ("epithet" → "title", "juridical" → "legal")
- Simpler word works ("utilize" → "use", "commence" → "start")
- It's academic showing-off ("hermeneutical" → "interpretation")

**Examples:**
- "liturgical practice" ✅ (keep - no simpler term)
- "the precise epithet" ❌ → "the precise title"
- "juridical hair-splitting" ❌ → "legal hair-splitting"
- "apocalyptically" ✅ (keep - domain standard)

## Greek, Hebrew, and Other Languages

**First mention of a foreign word:** Use transliteration with original script in parentheses.
```
\emph{porphyrous} (πορφυροῦς)
\emph{apokatastasis} (ἀποκατάστασις)
\emph{tekton} (τέκτων)
```

**Subsequent mentions:** Original script only is fine.
```
πορφυροῦς
```

**Longer fragments:** Original script first, then English translation.
```
τὸ πορφυροῦν αἷμα, "the purple of blood"
ἀνανέωσις τῆς ἀρχῆς, "renewal of the rule"
```

**Place names showing linguistic evolution:** Original script only is acceptable (they're proper nouns).
```
Ῥαμαθαΐμ → Ῥαμαθήμ → Ἀριμαθαία
```

## Red Flags = Stop

**Duplication:**
- Topic seems "important" (probably already covered)
- Famous text (Lord's Prayer, baptism)
- Mentioned in chapter title
