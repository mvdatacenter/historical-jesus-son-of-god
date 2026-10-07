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

3. **Read the output for stitching artifacts** - The script splits chapters into fragments. Read for:
   - Duplicate `\section{}` or `\subsection{}` headers at fragment boundaries
   - Stray ` ```latex` or ` ``` ` markers from ChatGPT formatting
   - Incomplete sentences at fragment joins
   - Missing or doubled text where fragments overlap
   - `\href{}` links - URL must stay intact, display text can be translated
   - `\includegraphics{}` paths - need the `../../` prefix (e.g., `assets/map` → `../../assets/map`)

4. **Read the grammar report** - LanguageTool flags many false positives (LaTeX, proper nouns), so review each.

5. **Fix in the script, then rerun** - A fix to a generated file goes into the script
   or the prompt, and the chapter is rerun. A stitching artifact is fixed in
   `translate_book.py`, where `fix_section_label_formatting()` fixes the split label;
   a wording or grammar pattern is fixed in the language's prompt in
   `create_translation_prompt()`. The per-language tables below list the patterns to
   read for.

## What a rerun writes, and what stays hand-authored

`translate_book.py --all` writes one file per English source it translates:
`preface_XX.tex`, `chapter1_XX.tex` through `chapter6_XX.tex`, and `epilogue_XX.tex`,
where `XX` is the first two letters of the language. `.gitattributes` marks those as
generated, and `translations/<language>/generated.json` is the record that makes the
marking hold. After writing a file the script records its sha256, the name and sha256
of the English source it was translated from, and `written_by`. On every pull request
`scripts/test_translate_book.py` reads the `.gitattributes` patterns and checks each
file they select. It fails a file with no entry, a file whose sha256 differs from the
recorded one, which is what a hand edit produces, and an entry whose file is gone.
While the recorded source sha256 still matches the English file, it also fails a
translation missing one of that source's `\label{}`, `\ref{}`, `\cite{}`, `\href{}`
URLs or `\includegraphics{}` paths; once the English is edited after the translation
was written, the translation answers the earlier source and that comparison waits for
a rerun.

The master stays hand-authored. `polish/manuscript_po.tex` carries the Polish chapter
titles, `\setmainlanguage{polish}`, the font path, and the
`\addbibresource{../../references.bib}` and `\printbibliography` calls that print the
same three-part reference list as the English edition. The pipeline leaves it alone,
so edit it directly.

The Polish chapters were translated from an English draft that predated the
manuscript's citations, so they carry few of the 341 the English edition now holds,
and they were edited by hand afterwards. Their eight entries in `polish/generated.json`
therefore carry `"source_sha256": null` and a `written_by` naming the commit they were
recorded from, since the English they answer is not known. Rerunning the pipeline
against the current English chapters closes the citation gap and replaces each entry
with the script's own record; `scripts/test_source_registry.py` holds every cited key
in a translated edition to the same `references.bib` and registry entries the English
edition uses (#175).

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
