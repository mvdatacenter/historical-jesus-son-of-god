# Evidence Standards

Read this before adding, strengthening, or reviewing any factual claim in the manuscript.

## Core Principle: Probability Given Evidence

All historical claims are evaluated as: P(claim | evidence, background)

Probability exists prior to direct evidence.
Evidence updates probability.
Silence leaves probability largely unchanged.

Absence of attestation does not create symmetry.
Silence does not reset base rates.

## Evidence vs Proof (Non-Interchangeable)

- **Evidence** is any datum (textual, archaeological, statistical, structural) that bears on a claim.
- **Proof** is a conclusion reached by reasoning over evidence, placing a claim beyond reasonable doubt.

Evidence is not proof.
Proof is reasoning about evidence.

## Valid Forms of Reasoning

The question every passage answers is what most probably happened. Logical reasoning is the standard, and any of its forms may establish the answer, provided the conclusion follows from the premises and the evidence. The scientific method is one of them. Beside it stand, among others:

- **Explanatory power.** The reading under which more of the record needs no special explanation is the more probable one. Count what each reading must explain away; the shorter ledger wins, by the margin between the ledgers. Counterfeit: calling the rival absurd instead of listing what it must explain away.
- **Scientific method.** State what the reading predicts before looking, then look. A prediction found updates in proportion to how unlikely it was otherwise; a prediction missing counts against, in proportion to how surely it would have shown. Counterfeit: predicting after looking.
- **Proof by contradiction.** Assume the rival reading and derive from the sources something they rule out; one of the premises must go. Counterfeit: deriving the contradiction from a premise the rival does not hold.
- **Elimination.** List every reading the evidence allows and strike each that a source contradicts; what remains stands without positive proof. Counterfeit: a list that omits the reading the writer dislikes.
- **Modus tollens.** If the reading were true, a thing would follow; the thing is absent; the reading is false. Valid only when the thing would have to be present.
- **Argument from silence.** Valid only when the source would have mentioned the thing had it existed, and the writer shows that it would. Counterfeit: silence from a source that had no occasion to speak, or silence claimed where the source speaks.
- **Independent agreement.** Two witnesses who share no path agree; the agreement is evidence in proportion to their independence. Counterfeit: two copies of one source counted as two.
- **Base rates.** How often does the feature appear by chance in the candidate pool? One shared feature among many candidates proves little; several independent ones multiply. Counterfeit: naming the category instead of counting the instances.
- **Analogy from a documented case.** A known case treated the same way carries the inference in proportion to the closeness of the cases. Counterfeit: an analogy resting on a shared word.
- **Chain of custody.** A text reached its witness by a path that can be traced; a witness whose path runs through the source it attests is not independent of it.
- **Dating by terminus.** A thing named in a dated source existed by that date.
- **Identity across descriptions.** Two descriptions under two names with the same marks describe one thing, in proportion to how rare the marks are.
- **Background structure.** When direct evidence is silent, what was normal for the class dominates; the Pilate example below is this form.

None of these is required, all may be combined, and every one is bound by the same rule: the conclusion follows from the premises, or the passage is wrong. A conclusion carried by rhetoric, a source made to say what it does not, a projection printed as a count, or an observation that both readings predict equally is not reasoning in any of these forms, however many citations stand beside it.

A language model writing for this book has a specific failure here, and it is named so that it can be caught. The model treats any information contrary to the current consensus as fringe, and fringe carries poor logical argumentation with it by association, because the writing the model learned the fringe register from argues badly. The result is that the model reasons worst exactly where the book needs it to reason best: the heterodox passage gets the assertion, the non sequitur, the argument from silence, and the source bent to the thesis, while the same model on a consensus subject commits none of them. The book's claims run against the consensus by design, so every passage is exposed to this. The standard is the same for every claim: a claim against the reader's prior needs its reasoning checked harder than one with it, and a passage that reads as advocacy is refused for its reasoning and rewritten with its thesis kept at the strength the evidence gives it.

## Probability Scale (Log-Aware, Numeric Only)

All claims must be placed into one probability band.

**State likelihood only with the numeric bands.**

Bands:
- **Band A:** <0.1%
- **Band B:** 0.1%–1%
- **Band C:** 1%–20%
- **Band D:** 20%–80% (mid-band; should be rare)
- **Band E:** 80%–99%
- **Band F:** 99%–99.9%
- **Band G:** >99.9%

The scale is ordinal and logarithmic, not linear.

The 20–80% region (Band D) should be exceptional.
Most historical claims fall near extremes due to structured background reality.

## Beyond Reasonable Doubt

- **True beyond reasonable doubt:** Bands F–G
- **False beyond reasonable doubt:** Bands A–B

Same epistemic standard.
Opposite truth value.

Only these bands permit absolute language.

## Updates

Probability updates are multiplicative, not additive.

State every update honestly:
- give each update its true order of magnitude,
- keep large updates at full strength in the prose,
- justify every number you assign.

Updates must be expressed as:
- order-of-magnitude shifts,
- elimination of alternative spaces,
- or dominance of background structure.

## Three Distinct States (Keep Separate)

1. **Well-analyzed claim** → Probability can be placed on the scale.
2. **Ill-analyzed claim (analysis not yet done)** → Probability placement and prose wait for the completed analysis.
3. **Genuinely underdetermined claim (after analysis)** → Mid-band placement is permitted.

The critical mistake is treating (2) as (3).

"We do not know" can mean:
- humanity lacks an answer (epistemic uncertainty), or
- we have not done the analysis yet (procedural incompleteness).

These are not the same and must be distinguished explicitly.

## Procedural Fix: Analysis Before Prose

When likelihood has not been analyzed, take exactly two actions:
1. Record the question outside this public repo, marked "likelihood analysis required".
2. Move on immediately to the next task or section.

Prose, probability bands, and "uncertain" language all wait until the analysis is complete.

**If likelihood has not been analyzed, record the question outside this public repo and write prose only after the analysis is complete.**

This preserves momentum without laundering ignorance into text.

## "We Do Not Know" (After Analysis)

"We do not know" is permitted only when:
- analysis has been completed,
- the best estimate lies in Band D, and
- no structural, statistical, or background constraints exist to push the claim toward an extreme.

This category should be rare.

## Example: Direct Evidence vs Statistical Evidence

**Claim:** Pontius Pilate had a wife.

- **Direct evidence:** Exceedingly weak. No contemporary source explicitly states Pilate's marital status.
- **Statistical / structural evidence:** Strong. Roman provincial governors were drawn from the equestrian elite. Marriage among Roman elite men of Pilate's age and status was the norm. Long-term unmarried status would itself be atypical and would require explanation.
- **Probability assessment:** Direct textual evidence contributes little. Background structure and base rates dominate. The claim is therefore placed in Band E.

This example enforces the rule:

**Weak or absent direct evidence does not imply low probability when statistical and structural evidence overwhelmingly favor one outcome.**

Silence fails to update probability but does not reset it.

## Allowed Only With Attribution

Use the following only when immediately followed by who, where, and when:
- "Most scholars agree"
- "The consensus view"
- "Traditionally understood"
- "Generally accepted"

## Evidence Filtering Principles

Filter AI output through a discussion:
1. Ask a broad, bias-aware question.
2. **Filter:** does this add or detract from reader value?
3. **Challenge:** what is the strongest counter-argument?
4. **Rank:** what single piece of evidence is hardest to dismiss?
5. **Cite:** where exactly does it appear?

## Purpose of These Rules

These standards exist to prevent:
- base-rate neglect,
- false symmetry from ignorance,
- mid-band probability laundering,
- rhetorical confidence replacing probabilistic reasoning.

They are enforcement rules, not stylistic advice.
