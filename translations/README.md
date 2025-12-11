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
