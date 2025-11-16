# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a scholarly book project titled "Historical Jesus as the Son of God: Glory to the Newborn King" that uses AI-assisted historical analysis to examine Jesus and early Christianity through a Greco-Christian rather than Judeo-Christian lens. The project is written in LaTeX and compiled to both PDF and HTML outputs.

## Build System

### Compiling the Book

The project uses **LuaLaTeX** or **XeLaTeX** (NOT pdflatex) due to custom font requirements:

```bash
# Compile the full manuscript to PDF
latexmk -lualatex manuscript.tex

# Or using xelatex
latexmk -xelatex manuscript.tex

# Output will be in: out/manuscript.pdf
```

The build configuration is in `.latexmkrc` and specifies that `xelatex` or `lualatex` should be used for all PDF compilation.

### Generating HTML

```bash
# Convert to HTML using pandoc
mkdir -p public
pandoc manuscript.tex -s --mathjax -o public/index.html
```

### Python Map Utility

```bash
# Generate interactive map of historical cities
python map.py

# Output: historical_cities_map.html
```

This uses Python 3.12.2+ with the `folium` library for geographical visualization.

## Architecture

### Document Structure

The main document is `manuscript.tex`, which orchestrates the entire book:

- **Preface**: `preface.tex` - Methodology, AI-assisted analysis approach, and project goals
- **Chapter 1**: `chapter1.tex` - "The Quest for the Historical Jesus" - Overview of scholarly portraits (apocalyptic prophet, revolutionary, etc.)
- **Chapter 2**: `chapter2.tex` - "Jesus Christ, Son of Joseph and Mary Christ"
- **Chapter 3**: `chapter3.tex` - "He Truly was the Son of God"
- **Chapter 4**: `chapter4.tex` - "Gospels as Historically Reliable Sources of Historical Jesus"
- **Chapter 5**: `chapter5.tex` - "Pauline Epistles to All Nations"
- **Chapter 6**: `chapter6.tex` - "The Purple Phoenix Raises"
- **Epilogue**: `epilogue.tex`

Each chapter is a standalone `.tex` file included via `\input{}` commands in `manuscript.tex`.

### Key Technical Requirements

1. **Engine**: Must use LuaLaTeX or XeLaTeX (the document enforces this with `\ifPDFTeX` check)
2. **Fonts**:
   - Main: EB Garamond
   - Greek: EB Garamond
   - Hebrew: SBL_Hbrw.ttf (in `fonts/` directory)
   - Math: Garamond-Math
3. **Languages**: English (main), Greek, Hebrew via `polyglossia` package
4. **Output Directory**: LaTeX auxiliary files go to `out/` (per `.latexmkrc`)

### Directory Structure

```
.
├── manuscript.tex          # Main LaTeX document
├── preface.tex            # Preface content
├── chapter[1-6].tex       # Chapter contents
├── epilogue.tex           # Epilogue content
├── fonts/                 # Custom fonts (SBL Hebrew)
├── assets/                # Images and other assets
├── auxil/                 # Auxiliary LaTeX build files
├── out/                   # Primary build output (PDF, synctex, aux, etc.)
├── docs/                  # Documentation (HTML output for web)
├── map.py                 # Python script to generate historical cities map
└── .github/workflows/ci.yml  # CI/CD for building and deploying
```

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on pushes to `main` or `html` branches:

1. **Build PDF**: Compiles `manuscript.tex` using LuaLaTeX
2. **Build HTML**: Converts to HTML using Pandoc with MathJax
3. **Deploy Pages**: Publishes HTML to GitHub Pages
4. **Create Release**: Creates automatic releases with PDF attached

## Content Focus

The book challenges mainstream scholarly consensus by:

- Examining Christianity's Greek institutional foundations rather than isolated rural cult origins
- Questioning dating and authorship of Gospels
- Exploring dynastic succession themes in baptism and other narratives
- Using AI to synthesize patterns across vast historical sources
- Focusing on Greco-Christian rather than Judeo-Christian interpretations

## Historical Cities Map

The `map.py` script generates an interactive Folium map of 40+ cities mentioned in the New Testament, including Jerusalem, Antioch, Ephesus, Rome, Athens, Corinth, etc. This supports the book's argument about Christianity's connection to Greek-speaking urban centers.

## Branch Strategy

- `main`: Primary development branch
- `acts-are-fiction`: Current working branch (feature branch)
- `html`: Branch for HTML-specific changes

## Important Notes

- When editing chapter content, preserve Greek and Hebrew text formatting
- The book uses scholarly citation conventions with footnotes
- Maintain academic tone focused on historical methodology
- AI is used as a research tool, not as a decision-maker or conclusion-drawer
- The project explicitly states it is not theological advocacy but historical inquiry
