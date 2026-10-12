# Build, Scripts and CI

How the manuscript is built, what `scripts/` holds, and what the GitHub workflows run. Read this before building the book, touching `scripts/`, or changing a workflow.

## Build System

```bash
latexmk -lualatex manuscript.tex   # PDF → out/manuscript.pdf (LuaLaTeX or XeLaTeX only)
pandoc manuscript.tex -s --mathjax -o public/index.html   # HTML
python map.py                      # Historical cities map → historical_cities_map.html
```

Fonts: EB Garamond (main/Greek), SBL Hebrew, Garamond-Math; languages via `polyglossia`; LaTeX aux files go to `out/` (per `.latexmkrc`). Preserve Greek/Hebrew text formatting when editing.

`manuscript.tex` includes `preface.tex`, `chapter1.tex`–`chapter6.tex`, and `epilogue.tex`; images live in `assets/`, fonts in `fonts/`.

## Scripts

`scripts/` holds the citation pipeline (`source_registry.py`, `download_sources.py`, `verify_citations.py`, `review_citations.py`, `manual_review.py`, `verify_modern_works.py`, `add_llm_evaluations.py`), the translation pipeline (`translate_book.py`, output under `translations/`), and the audiobook pipeline (`tts_openai.py`, `audiobook_release.py`). The `chatgpt` CLI is documented in `ai-governance.md`.

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
