# Translations

## Process

1. **Run translation script**
   ```bash
   poetry run python scripts/translate_book.py chapter1.tex --lang polish --output-dir translations/polish
   ```
   This uses the ChatGPT Desktop app via macOS Accessibility API.

2. **Run grammar checker**
   ```bash
   poetry run python -c "
   import requests
   with open('translations/polish/chapter1_po.tex') as f:
       text = f.read()
   r = requests.post('https://api.languagetool.org/v2/check',
                     data={'text': text[:15000], 'language': 'pl'})
   for m in r.json().get('matches', []):
       print(m['message'], m.get('replacements', [])[:2])
   "
   ```

3. **Fix stitching artifacts** - The script splits chapters into fragments. Check for:
   - Duplicate `\section{}` or `\subsection{}` headers at fragment boundaries
   - Stray ` ```latex` or ` ``` ` markers from ChatGPT formatting
   - Incomplete sentences at fragment joins
   - Missing or doubled text where fragments overlap
   - Check `\href{}` links - URL must stay intact, display text can be translated
   - Fix `\includegraphics{}` paths - add `../../` prefix (e.g., `assets/map` → `../../assets/map`)

4. **Fix grammar errors** - LanguageTool flags many false positives (LaTeX, proper nouns), so review each.

5. **Common fixes by language** - see below.

## What a rerun writes, and what stays hand-authored

`translate_book.py --all` writes one file per English source it translates:
`preface_XX.tex`, `chapter1_XX.tex` through `chapter6_XX.tex`, and `epilogue_XX.tex`,
where `XX` is the first two letters of the language. `.gitattributes` marks those as
generated, which records where they come from while leaving them open to hand work:
steps 3 to 5 above are applied after every run.

The master stays hand-authored. `polish/manuscript_po.tex` carries the Polish chapter
titles, `\setmainlanguage{polish}`, the font path, and the
`\addbibresource{../../references.bib}` and `\printbibliography` calls that print the
same three-part reference list as the English edition. The pipeline leaves it alone,
so edit it directly.

The Polish chapters were translated from an English draft that predated the
manuscript's citations, so they carry few of the 341 the English edition now holds.
Rerunning the pipeline against the current English chapters is what closes that gap;
`scripts/test_source_registry.py` holds every cited key in a translated edition to the
same `references.bib` and registry entries the English edition uses (#175).

---

## Polish (polish/)

Common errors after ChatGPT translation:

| Error Type | Wrong | Correct |
|------------|-------|---------|
| Accusative -ia nouns | `eschatologie` | `eschatologię` |
| Accusative -ca nouns | `przywódce` | `przywódcę` |
| Preposition before w- | `z Wschodu` | `ze Wschodu` |
| Preposition before w- | `w wspólnotowym` | `we wspólnotowym` |
| Pleonasm | `autentyczne fakty` | `fakty` |
| Capitalization | `Kaplicy Greckiej` | `kaplicy greckiej` |

LanguageTool false positives to ignore:
- Latin/Greek terms (Christos, YHWH, Via Maris)
- Proper nouns (Ptolemeusze, Hillel)
- LaTeX commands (`\emph{}`, `\section{}`)
