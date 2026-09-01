# Historical Jesus as the Son of God: Glory to the Newborn King

This book presents a perspective on the historical Jesus Christ as the Son of God. 
It is a unique attempt to portray Jesus as Christ and the Gospels as reliable historical sources, guided by rigorous historical method, without bias or theological presupposition.

By “historical method,” we mean the effort to determine what most probably happened — which, by definition, excludes supernatural explanations.
This is not a theological work, and it does not aim to change the reader’s religious beliefs.
Rather, it seeks to offer a new framework that both deeply committed Christians and those with no religious affiliation — whether casual readers or professional scholars — may find intellectually valuable.
While we do not seek to challenge anyone’s faith, we do seek to challenge assumptions widely held about the story of Jesus and his early followers.
Our aim is to invite readers to confront new and important questions about the historical Jesus and the origins of Christianity.

The central methodology of this project is the use of the world’s most advanced artificial intelligence to examine an enormous body of historical sources and scholarly literature — far beyond what any human could process in a lifetime.
This enables us to identify patterns, contradictions, and questions that have often remained hidden in plain sight, were forgotten, or were curiously overlooked in mainstream discussions.

The most prominent pattern emerging from this analysis is a strong and persistent modern theological and scholarly consensus in favor of Judeo-Christian interpretations — even in cases where the historical evidence overwhelmingly supports a Greco-Christian perspective.
A second major pattern is the continued reliance on early Christian scholars from past centuries who worked with far more limited sources and tools, yet remain virtually immune to critique as the founding authorities of the scholarly tradition.
The third major pattern is the tendency to deny any possibility of Christianity’s institutional foundations, treating it instead as an isolated rural cult that began from zero with Jesus and John the Baptist.

Some examples of central but nearly overlooked questions pointing to a Greco-Christian rather than Judeo-Christian historical interpretation include:
* Why does the list of cities mentioned in the New Testament so closely match the list of the most important Greek-speaking cities of the time? - Perhaps Christianity has more to do with the continuation of Greek empire than has been proposed so far.
* Why do the allegedly much-later names of the Magi closely resemble imperial court titles from an earlier era? - Perhaps some elements of the biblical story that are often unequivocally considered late legendary inventions have more to them than meets the eye?
 
There are many questions that are already well known but can be brought into a new light by considering them in Greek-Christian context:
* Why do many early Gospel manuscripts describe Jesus’s baptism with the words, ‘You are my Son. Today I have begotten you’? - Can the baptism of Jesus be understood as a dynastic succession rite commonly described in by Greek royal historians?
* Why is Thomas portrayed as the doubter? - Can Thomas’s behavior be grounded in dynastic succession?

Beyond identifying questions, AI tools are also highly effective at spotting contradictions and inconsistencies in the traditional narratives. 
In particular, we revisit the mainstream scholarship consensus on issues such as the dating and authorship of the Gospels and the original structure of the earliest Christian movement.
Examples of issues that seem to have a strong body of evidence behind them, but are nearly inexplicably dismissed in favor of alternatives with far poorer evidence, include:
* Johannine primacy and authorship - Was the author of John a woman and a direct eye-witness to the events described in the Gospels?
* Late dating of Jesus’s birth - Can there be a plausible explanation for the deep discrepancies in the biblical birth narratives of Jesus?

While not every question has a certain answer, this project ultimately aims to spark curiosity, deepen engagement with the Christian story, and inspire a renewed search for understanding through historical inquiry.

> At this stage, our goal is to list and briefly comment on these questions and discrepancies. The overall narrative flow is still a work in progress, and we will continue to refine it as we gather more insights from the AI and from our own research.

# Research Boundary

Exploratory research belongs outside this public repository until it is ready for publication.
This public repository should receive research work only after it becomes a citation record, bibliography entry, verified source passage, or code or data directly used to construct a result included here.
Solar-eclipse investigations, Pauline-location maps, generated findings, and similar exploratory artifacts stay outside this repository until they become verified citation material or reproducible result-building code.
Detailed research history, per-chapter Q&A, open research gaps, and Alexandria findings triage live in the private `historical-jesus-son-of-god-research` repo; findings pass through its review workflow, then through the public citation verification pipeline, before entering manuscript prose.
This repo accepts external contributions; keep proprietary data sources and extraction targets in internal materials, and use public-safe research summaries in public-facing files.

# Table of Contents

- [Preface](preface.tex)
- [Chapter 1: Jesus Christ, Son of Joseph and Mary Christ](chapter1.tex)
- [Chapter 2: Jesus Christ, Son of Joseph and Mary Christ](chapter2.tex)
- [Chapter 3: He Truly was the Son of God](chapter3.tex)
- [Chapter 4: Gospels are Historically Reliable](chapter4.tex)
- [Chapter 5: Pauline Epistles to All Nations](chapter5.tex)
- [Chapter 6: The Purple Phoenix Raises Again](chapter6.tex)

© 2025 MV Data sp. z o.o. . All rights reserved.

# Working on This Repository

## Critical Rules

TELL THE TRUTH AT ALL COST.
DO THE COMPLETE WORK EVERY TIME.
FOLLOW THE INSTRUCTIONS CLOSELY.

**When the user says "stop", "STOP", or any variation: stop immediately.** Halt mid-action: leave the current action unfinished — even "just this one thing" — hold every further tool call, and wait for instructions. The user sees something you don't. STOP MEANS STOP.

## Detailed Guidance (read before the matching work)

| Doc | Read before |
|-----|-------------|
| [docs/ai-governance.md](docs/ai-governance.md) | Any ChatGPT use: governance model, mandatory Claude review, bias handling, prompt templates, the ChatGPT CLI, and engineering-safety conduct |
| [docs/writing-standards.md](docs/writing-standards.md) | Writing or reviewing manuscript prose: citation style, scholar-name rules, the AI-garbage definition, jargon, Greek/Hebrew formatting |
| [docs/evidence-standards.md](docs/evidence-standards.md) | Adding or judging factual claims: probability bands, evidence vs proof, attribution rules for consensus phrasing |
| [docs/DD_0001_citation-review-report.md](docs/DD_0001_citation-review-report.md) | Accepting any new factual claim: the download → locate → semantic-review pipeline |
| [docs/REVIEW.md](docs/REVIEW.md) | Reviewing a PR that changes the manuscript |

## Adding Content to Chapters

The project treats ChatGPT as the generator and Claude as the reviewer; any non-trivial ChatGPT output must pass Claude review (`docs/ai-governance.md`).
For public chapter edits: verify claims against primary sources, keep the chapter's existing argument structure central, and run the citation verification pipeline before accepting new factual claims.
Extended Alexandria findings are reviewed in the private `historical-jesus-son-of-god-research` repo before they become public manuscript work.

## Build System

```bash
latexmk -lualatex manuscript.tex   # PDF → out/manuscript.pdf (LuaLaTeX or XeLaTeX only)
pandoc manuscript.tex -s --mathjax -o public/index.html   # HTML
python map.py                      # Historical cities map → historical_cities_map.html
```

Fonts: EB Garamond (main/Greek), SBL Hebrew, Garamond-Math; languages via `polyglossia`; LaTeX aux files go to `out/` (per `.latexmkrc`). Preserve Greek/Hebrew text formatting when editing.

`manuscript.tex` includes `preface.tex`, `chapter1.tex`–`chapter6.tex`, and `epilogue.tex`; images live in `assets/`, fonts in `fonts/`.

## Scripts

`scripts/` holds the citation pipeline (`source_registry.py`, `download_sources.py`, `verify_citations.py`, `review_citations.py`, `manual_review.py`, `verify_modern_works.py`, `add_llm_evaluations.py`), the translation pipeline (`translate_book.py`, output under `translations/`), and the audiobook pipeline (`tts_openai.py`, `audiobook_release.py`). The `chatgpt` CLI is documented in `docs/ai-governance.md`.

Generated reports: `sources/citation_review.html` (gitignored) and `sources/verification_report.md`.

## CI/CD

Build and publish (`.github/workflows/ci.yml`), on `main`/`html` branches:
1. Build PDF (LuaLaTeX)
2. Build HTML (Pandoc + MathJax)
3. Deploy to GitHub Pages
4. Create release with PDF

Tests (`.github/workflows/tests.yml`), on `main`/`html` and on pull requests:
runs `pytest` over `scripts/`. It triggers on changes to `scripts/`, the files
the citation invariants scan (`preface.tex`, `chapter*.tex`, `epilogue.tex`,
`translations/`), `references.bib`, and the workflow itself, so it runs exactly
when its result can change. It pip-installs pytest, `requests`, and
`beautifulsoup4` directly and holds read-only permissions, since it runs on
pull requests from forks. Installing directly keeps the job independent of
Poetry, whose `tychicus` pin resolves over a private SSH remote that requires
org credentials.

## Branch Strategy

- `main`: Primary development
- **Every change reaches `main` through a PR** - create PRs, and merge only when instructed

## Docs Folder

`docs/` holds the guidance files above plus design documents (`DD_NNNN_*.md`) and post-mortems (`PM_NNNN_*.md`), sequentially numbered with descriptive titles.

## Content Focus

Challenges mainstream consensus by examining:
- Greek institutional foundations (not isolated rural cult)
- Dynastic succession themes
- Greco-Christian lens (not Judeo-Christian)

AI is a research tool, not a decision-maker; the book is historical inquiry, not theological advocacy.
