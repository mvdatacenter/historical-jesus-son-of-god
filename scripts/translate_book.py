#!/usr/bin/env python3
"""
translate_book.py

Translate LaTeX book chapters to another language using ChatGPT Desktop App.

Features:
  - Reads LaTeX chapters and splits them into manageable fragments
  - Sends each fragment to ChatGPT for translation
  - Preserves LaTeX formatting and commands
  - Writes translated output to new files
  - Supports recovering fragments from ChatGPT conversation (--recover)

Usage:
  poetry run python scripts/translate_book.py chapter1.tex --lang Polish
  poetry run python scripts/translate_book.py chapter1.tex --lang Polish --recover
  poetry run python scripts/translate_book.py --all --lang Polish
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional
import json
import shutil

# Import send_prompt from the chatgpt module
from chatgpt_desktop import send_prompt


def extract_fingerprints(text: str) -> dict:
    """Extract structural fingerprints from LaTeX text.

    Fingerprints are elements that MUST survive translation unchanged.
    Even if 10% of text is lost, these should still match.

    Returns dict with:
        - labels: set of \\label{} values (never translated)
        - refs: set of \\ref{} values (never translated)
        - cites: set of \\cite{} keys (never translated)
        - urls: set of URLs from \\href{} (never translated)
        - images: set of \\includegraphics{} paths (never translated)
        - greek_strings: set of Greek Unicode text (preserved exactly)
        - hebrew_strings: set of Hebrew Unicode text (preserved exactly)
        - numbers: set of significant numbers (years, verses, etc.)
        - command_counts: dict of LaTeX command counts
    """
    fingerprints = {
        'labels': set(),
        'refs': set(),
        'cites': set(),
        'urls': set(),
        'images': set(),
        'greek_strings': set(),
        'hebrew_strings': set(),
        'numbers': set(),
        'command_counts': {},
    }

    # \label{...} - never translated
    for match in re.finditer(r'\\label\{([^}]+)\}', text):
        fingerprints['labels'].add(match.group(1))

    # \ref{...} - never translated
    for match in re.finditer(r'\\ref\{([^}]+)\}', text):
        fingerprints['refs'].add(match.group(1))

    # \cite{...} - never translated (may have multiple keys)
    for match in re.finditer(r'\\cite\{([^}]+)\}', text):
        for key in match.group(1).split(','):
            fingerprints['cites'].add(key.strip())

    # \href{URL}{...} - URL never translated
    for match in re.finditer(r'\\href\{([^}]+)\}\{', text):
        fingerprints['urls'].add(match.group(1))

    # \includegraphics{...} or \includegraphics[...]{...} - path never translated
    for match in re.finditer(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text):
        fingerprints['images'].add(match.group(1))

    # Greek Unicode text (U+0370-03FF basic, U+1F00-1FFF extended)
    for match in re.finditer(r'[\u0370-\u03FF\u1F00-\u1FFF]{2,}', text):
        fingerprints['greek_strings'].add(match.group(0))

    # Hebrew Unicode text (U+0590-05FF)
    for match in re.finditer(r'[\u0590-\u05FF]{2,}', text):
        fingerprints['hebrew_strings'].add(match.group(0))

    # Significant numbers: years (4 digits), verse refs (N:N), standalone numbers
    # Years: 4-digit numbers that look like years (70-2100 range plausible)
    for match in re.finditer(r'\b(\d{4})\b', text):
        year = int(match.group(1))
        if 1 <= year <= 2100:
            fingerprints['numbers'].add(match.group(1))

    # Verse references: N:N or N:N-N patterns
    for match in re.finditer(r'\b(\d{1,3}:\d{1,3}(?:-\d{1,3})?)\b', text):
        fingerprints['numbers'].add(match.group(1))

    # BCE/CE years: "N BCE" or "N CE"
    for match in re.finditer(r'\b(\d{1,4})\s*(?:BCE|CE|BC|AD)\b', text, re.IGNORECASE):
        fingerprints['numbers'].add(match.group(1))

    # Command counts - count occurrences of key LaTeX commands
    commands_to_count = ['section', 'subsection', 'subsubsection',
                         'footnote', 'emph', 'textit', 'textbf', 'textgreek']
    for cmd in commands_to_count:
        count = len(re.findall(rf'\\{cmd}\{{', text))
        if count > 0:
            fingerprints['command_counts'][cmd] = count

    return fingerprints


def fingerprint_similarity(source_fp: dict, translated_fp: dict) -> float:
    """Calculate similarity score for MATCHING translations to sources.

    PURPOSE: Find which translation belongs to which source fragment.
    This is a matching heuristic only - NOT acceptance criteria.

    WHY THIS IS NOT VALIDATION:
    An approximate validator is not a good validator. If you accept
    "90% match", you're accepting 10% missing content. That's not
    validation - that's guessing. Validation must be binary: valid or not.

    Returns 0.0-1.0 based on fingerprint overlap.
    """
    total = 0
    matched = 0

    # Labels are AUTHORITATIVE - if source has labels but none match, reject immediately
    if source_fp['labels']:
        label_matches = len(source_fp['labels'] & translated_fp['labels'])
        if label_matches == 0:
            return 0.0  # Wrong fragment - labels don't match at all
        total += len(source_fp['labels'])
        matched += label_matches

    # Greek/Hebrew/Numbers - count similarity
    for key in ['greek_strings', 'hebrew_strings', 'numbers']:
        src_count = len(source_fp[key])
        tgt_count = len(translated_fp[key])
        if src_count > 0:
            total += src_count
            matched += min(src_count, tgt_count)

    # Commands - count similarity
    for cmd, count in source_fp['command_counts'].items():
        total += count
        matched += min(count, translated_fp['command_counts'].get(cmd, 0))

    return matched / total if total > 0 else 0.0


def validate_label_attachment(text: str) -> List[str]:
    r"""Validate that section/paragraph labels are attached to their headers.

    A lone \label{sec:...}, \label{subsec:...}, or \label{par:...} on its own line
    (not preceded by corresponding command on same line) indicates ChatGPT split them.

    Returns list of errors (empty if valid).
    """
    errors = []
    lines = text.split('\n')

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check for section/subsection/paragraph labels that should be attached
        # Matches: \label{sec:...}, \label{subsec:...}, \label{subsubsec:...}, \label{par:...}
        if re.match(r'^\\label\{(sub)*(sec|par):', stripped):
            # This label is on its own line - it should be attached to a section/paragraph
            errors.append(f"detached label on line {i+1}: {stripped[:50]}")

    return errors


def validate_fingerprints(source_fp: dict, translated_fp: dict, verbose: bool = False, translated_text: str = None) -> Tuple[bool, List[str]]:
    r"""Validate that translation matches source.

    PHILOSOPHY:
    A validator is only useful if it reliably detects missing content.
    An uncertain validator creates false positives and wastes effort.

    VALIDATORS:
    - labels: \label{} tags are never translated. Missing = missing section.
    - refs: \ref{} references are never translated.
    - cites: \cite{} keys are never translated.
    - urls: URLs in \href{} are never translated.
    - images: \includegraphics{} paths are never translated.
    - greek count: Greek text count.
    - hebrew count: Hebrew text count.
    - command counts: \emph{}, \textit{}, etc.
    - label attachment: \label{sec:...} must be on same line as \section{}.

    BAD VALIDATORS (not used):
    - numbers count: In Polish, numbers are often written as words
      (e.g., "42" → "czterdzieści dwa"), so digit counts don't match.

    Returns (is_valid, errors):
    - is_valid: True if all validators pass
    - errors: List of what's wrong
    """
    errors = []

    # String identifiers must match exactly
    for name, key in [('labels', 'labels'), ('refs', 'refs'), ('cites', 'cites'),
                      ('urls', 'urls'), ('images', 'images')]:
        if source_fp[key]:
            missing = source_fp[key] - translated_fp[key]
            if missing:
                errors.append(f"{name}: missing {list(missing)}")

    # Check label attachment if translated text is provided
    if translated_text:
        attachment_errors = validate_label_attachment(translated_text)
        errors.extend(attachment_errors)

    # Counts must match
    for name, key in [('greek', 'greek_strings'), ('hebrew', 'hebrew_strings')]:
        src_count = len(source_fp[key])
        tgt_count = len(translated_fp[key])
        if src_count != tgt_count:
            errors.append(f"{name}: count {src_count}→{tgt_count}")

    # Command counts must match
    src_counts = source_fp['command_counts']
    tgt_counts = translated_fp['command_counts']
    for cmd in set(src_counts.keys()) | set(tgt_counts.keys()):
        src_count = src_counts.get(cmd, 0)
        tgt_count = tgt_counts.get(cmd, 0)
        if src_count != tgt_count:
            errors.append(f"{cmd}: {src_count}→{tgt_count}")

    if verbose and errors:
        for err in errors:
            print(f"      ✗ {err}", file=sys.stderr)

    return len(errors) == 0, errors


def match_translations_to_sources(
    source_fragments: List[str],
    translated_texts: List[str]
) -> List[Tuple[int, str, float]]:
    """Match translated texts to source fragments using fingerprinting.

    Args:
        source_fragments: List of source LaTeX fragments
        translated_texts: List of translated texts (order unknown)

    Returns:
        List of (fragment_index, translated_text, confidence) tuples.
        fragment_index is 1-based. Only includes matches with confidence > 0.5.
    """
    # Extract fingerprints for all sources
    source_fps = [(i+1, extract_fingerprints(frag)) for i, frag in enumerate(source_fragments)]

    # Extract fingerprints for all translations
    translated_fps = [(text, extract_fingerprints(text)) for text in translated_texts]

    matches = []
    used_sources = set()
    used_translations = set()

    # Find best matches greedily (highest similarity first)
    all_pairs = []
    for src_idx, src_fp in source_fps:
        for t_idx, (t_text, t_fp) in enumerate(translated_fps):
            similarity = fingerprint_similarity(src_fp, t_fp)
            if similarity > 0:  # Any match at all
                all_pairs.append((similarity, src_idx, t_idx, t_text))

    # Sort by score descending
    all_pairs.sort(reverse=True, key=lambda x: x[0])

    # Greedy matching - fingerprint score is the validation
    for score, src_idx, t_idx, t_text in all_pairs:
        if src_idx in used_sources or t_idx in used_translations:
            continue

        used_sources.add(src_idx)
        used_translations.add(t_idx)
        matches.append((src_idx, t_text, score))

    return sorted(matches, key=lambda x: x[0])


# Fragment size in characters (~500 lines, ChatGPT handles large context well)
DEFAULT_FRAGMENT_SIZE = 15000

# Languages supported
SUPPORTED_LANGUAGES = {
    "polish": "Polish",
    "pl": "Polish",
    "german": "German",
    "de": "German",
    "french": "French",
    "fr": "French",
    "spanish": "Spanish",
    "es": "Spanish",
    "italian": "Italian",
    "it": "Italian",
    "portuguese": "Portuguese",
    "pt": "Portuguese",
    "russian": "Russian",
    "ru": "Russian",
    "chinese": "Chinese (Simplified)",
    "zh": "Chinese (Simplified)",
    "japanese": "Japanese",
    "ja": "Japanese",
}


def normalize_language(lang: str) -> str:
    """Normalize language name to standard form."""
    lang_lower = lang.lower().strip()
    if lang_lower in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[lang_lower]
    # If not found, assume it's already the full language name
    return lang.strip()


def split_into_fragments(content: str, max_size: int = DEFAULT_FRAGMENT_SIZE) -> List[str]:
    """Split LaTeX content into fragments at natural boundaries.

    Tries to split at:
    1. Section boundaries (\\section, \\subsection, etc.)
    2. Paragraph boundaries (blank lines)
    3. Sentence boundaries (. followed by space/newline)

    Never splits in the middle of:
    - LaTeX commands
    - Greek/Hebrew text blocks
    """
    fragments = []

    # First, try to split at major section boundaries
    section_pattern = r'(\\(?:sub)*section\{[^}]+\})'
    parts = re.split(section_pattern, content)

    current_fragment = ""

    for part in parts:
        # If adding this part would exceed max_size, save current and start new
        if len(current_fragment) + len(part) > max_size and current_fragment:
            # Try to find a good split point within current_fragment
            if len(current_fragment) > max_size:
                # Split at paragraph boundaries
                sub_fragments = split_at_paragraphs(current_fragment, max_size)
                fragments.extend(sub_fragments[:-1])
                current_fragment = sub_fragments[-1] if sub_fragments else ""
            else:
                fragments.append(current_fragment.strip())
                current_fragment = ""

        current_fragment += part

    # Don't forget the last fragment
    if current_fragment.strip():
        if len(current_fragment) > max_size:
            sub_fragments = split_at_paragraphs(current_fragment, max_size)
            fragments.extend(sub_fragments)
        else:
            fragments.append(current_fragment.strip())

    return [f for f in fragments if f.strip()]


def split_at_paragraphs(content: str, max_size: int) -> List[str]:
    """Split content at paragraph boundaries (blank lines)."""
    paragraphs = re.split(r'\n\s*\n', content)

    fragments = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 > max_size and current:
            fragments.append(current.strip())
            current = para
        else:
            if current:
                current += "\n\n" + para
            else:
                current = para

    if current.strip():
        fragments.append(current.strip())

    return fragments


def get_cache_dir(output_dir: str, chapter_name: str) -> Path:
    """Get the fragment cache directory for a chapter."""
    return Path(output_dir) / ".fragments" / chapter_name


def get_cache_metadata_path(cache_dir: Path) -> Path:
    """Get the metadata file path for fragment cache."""
    return cache_dir / "metadata.json"


def save_fragment_to_cache(cache_dir: Path, fragment_num: int, source: str, translated: str) -> None:
    """Save a translated fragment to cache."""
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Save the translated fragment
    fragment_path = cache_dir / f"fragment_{fragment_num:03d}.tex"
    with open(fragment_path, 'w', encoding='utf-8') as f:
        f.write(translated)

    # Update metadata
    metadata_path = get_cache_metadata_path(cache_dir)
    metadata = {}
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

    if "fragments" not in metadata:
        metadata["fragments"] = {}

    metadata["fragments"][str(fragment_num)] = {
        "source_length": len(source),
        "translated_length": len(translated),
        "timestamp": time.time()
    }

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"  [Cache] Saved fragment {fragment_num} ({len(translated)} chars)", file=sys.stderr)


def load_cached_fragments(cache_dir: Path, source_fragments: List[str]) -> Tuple[List[Optional[str]], int]:
    """Load cached fragments and determine resume point.

    Returns:
        Tuple of (list of translated fragments or None for missing, first fragment to translate)
    """
    metadata_path = get_cache_metadata_path(cache_dir)

    if not cache_dir.exists() or not metadata_path.exists():
        return [None] * len(source_fragments), 1

    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    cached_fragments = metadata.get("fragments", {})
    translated = []
    resume_from = len(source_fragments) + 1  # Default: all done

    for i, source in enumerate(source_fragments, 1):
        fragment_path = cache_dir / f"fragment_{i:03d}.tex"
        cache_info = cached_fragments.get(str(i))

        if fragment_path.exists() and cache_info:
            # Validate: check if source length matches and translation isn't suspiciously short
            source_len = len(source)
            cached_source_len = cache_info.get("source_length", 0)

            # Source must match (within 5% to account for minor edits)
            source_match = abs(source_len - cached_source_len) / max(source_len, 1) < 0.05

            if not source_match:
                print(f"  [Cache] Fragment {i} source changed, needs re-translation", file=sys.stderr)
                translated.append(None)
                if resume_from > i:
                    resume_from = i
                continue

            # Load and validate using fingerprints
            with open(fragment_path, 'r', encoding='utf-8') as f:
                cached_translation = f.read()

            src_fp = extract_fingerprints(source)
            tgt_fp = extract_fingerprints(cached_translation)

            # Validate: 100% or reject
            is_valid, errors = validate_fingerprints(src_fp, tgt_fp, translated_text=cached_translation)

            if is_valid:
                print(f"  [Cache] Fragment {i}: 100% ✓", file=sys.stderr)
                translated.append(cached_translation)
            else:
                print(f"  [Cache] Fragment {i}: INVALID - needs re-translation:", file=sys.stderr)
                validate_fingerprints(src_fp, tgt_fp, verbose=True, translated_text=cached_translation)
                translated.append(None)
                if resume_from > i:
                    resume_from = i
        else:
            translated.append(None)
            if resume_from > i:
                resume_from = i

    return translated, resume_from


def clear_cache(cache_dir: Path) -> None:
    """Clear the fragment cache for a chapter."""
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        print(f"  [Cache] Cleared cache: {cache_dir}", file=sys.stderr)


def scrape_conversation_to_cache(cache_dir: Path, source_fragments: List[str]) -> int:
    """Scrape ChatGPT conversation and save translated fragments to cache.

    Uses fingerprint matching to correctly identify which translation
    corresponds to which source fragment, regardless of conversation order.

    Returns the number of fragments recovered.
    """
    from chatgpt_desktop import find_chatgpt_app, collect_turns_incrementally
    import tempfile

    ax_app, ns_app = find_chatgpt_app()
    if not ax_app:
        print("  [Scrape] ChatGPT app not found, skipping conversation recovery", file=sys.stderr)
        return 0

    # Collect turns
    temp_dir = tempfile.mkdtemp(prefix="translate_recover_")
    turns = []

    try:
        # Request more turns than fragments to handle conversation noise
        num_turns = len(source_fragments) + 5
        turns = collect_turns_incrementally(ax_app, ns_app, num_turns, temp_dir, debug=False)
        print(f"  [Scrape] Collected {len(turns)} turns from conversation", file=sys.stderr)
    except Exception as e:
        print(f"  [Scrape] Collection stopped: {e}", file=sys.stderr)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return 0
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    # Extract translated texts from assistant messages
    translated_texts = []
    for turn in turns:
        assistant_msg = turn.get('assistant', '')

        # Extract LaTeX from response
        code_match = re.search(r'```(?:latex)?\s*\n(.*?)\n```', assistant_msg, re.DOTALL)
        if code_match:
            translated = code_match.group(1).strip()
        else:
            translated = re.sub(r'^```(?:latex)?\s*\n?', '', assistant_msg)
            translated = re.sub(r'\n?```\s*$', '', translated).strip()

        if len(translated) > 100:  # Skip very short responses
            # Fix section/label formatting issues
            translated = fix_section_label_formatting(translated)
            translated_texts.append(translated)

    print(f"  [Scrape] Extracted {len(translated_texts)} candidate translations", file=sys.stderr)

    # Match translations to sources using fingerprinting
    matches = match_translations_to_sources(source_fragments, translated_texts)

    print(f"  [Scrape] Matched {len(matches)} fragments by fingerprint", file=sys.stderr)

    # Save matched fragments to cache
    recovered = 0
    for frag_idx, translated, confidence in matches:
        source = source_fragments[frag_idx - 1]
        print(f"  [Scrape] Fragment {frag_idx}: matched with {confidence:.0%} confidence ({len(translated)} chars)", file=sys.stderr)
        save_fragment_to_cache(cache_dir, frag_idx, source, translated)
        recovered += 1

    # Report unmatched fragments
    matched_indices = {m[0] for m in matches}
    unmatched = [i+1 for i in range(len(source_fragments)) if i+1 not in matched_indices]
    if unmatched:
        print(f"  [Scrape] Unmatched fragments: {unmatched}", file=sys.stderr)

    return recovered


def show_cache_status(input_file: str, output_dir: str, fragment_size: int) -> None:
    """Show the status of cached fragments for a chapter."""
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"ERROR: File not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fragments = split_into_fragments(content, fragment_size)
    cache_dir = get_cache_dir(output_dir, input_path.stem)

    print(f"\nCache status for {input_path.name}:", file=sys.stderr)
    print(f"  Source: {len(content)} chars, {len(fragments)} fragments", file=sys.stderr)
    print(f"  Cache dir: {cache_dir}", file=sys.stderr)

    if not cache_dir.exists():
        print(f"  Status: No cache exists", file=sys.stderr)
        return

    metadata_path = get_cache_metadata_path(cache_dir)
    if not metadata_path.exists():
        print(f"  Status: Cache dir exists but no metadata", file=sys.stderr)
        return

    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    cached_fragments = metadata.get("fragments", {})

    print(f"\n  {'Frag':<6} {'Source':<10} {'Cached':<10} {'Match':<8} {'Status':<12}", file=sys.stderr)
    print(f"  {'-'*6} {'-'*10} {'-'*10} {'-'*8} {'-'*12}", file=sys.stderr)

    good = 0
    bad = 0
    missing = 0

    for i, source in enumerate(fragments, 1):
        fragment_path = cache_dir / f"fragment_{i:03d}.tex"
        cache_info = cached_fragments.get(str(i))
        source_len = len(source)

        if fragment_path.exists() and cache_info:
            cached_source_len = cache_info.get("source_length", 0)
            translated_len = cache_info.get("translated_length", 0)

            # Check if source changed
            source_match = abs(source_len - cached_source_len) / max(source_len, 1) < 0.05

            if not source_match:
                status = "⚠ SRC CHANGED"
                bad += 1
                print(f"  {i:<6} {source_len:<10} {translated_len:<10} {'—':<8} {status:<12}", file=sys.stderr)
                continue

            # Validate: 100% or invalid
            with open(fragment_path, 'r', encoding='utf-8') as f:
                cached_translation = f.read()

            src_fp = extract_fingerprints(source)
            tgt_fp = extract_fingerprints(cached_translation)
            is_valid, errors = validate_fingerprints(src_fp, tgt_fp, translated_text=cached_translation)

            if is_valid:
                status = "✓ VALID"
                good += 1
            else:
                status = f"✗ INVALID"
                bad += 1

            print(f"  {i:<6} {source_len:<10} {translated_len:<10} {status:<12}", file=sys.stderr)

            # Show errors for invalid
            if not is_valid:
                validate_fingerprints(src_fp, tgt_fp, verbose=True, translated_text=cached_translation)
        else:
            missing += 1
            print(f"  {i:<6} {source_len:<10} {'—':<10} {'—':<8} {'✗ MISSING':<12}", file=sys.stderr)

    print(f"\n  Summary: {good} OK, {bad} invalid, {missing} missing", file=sys.stderr)
    if bad > 0 or missing > 0:
        print(f"  Run with --recover to translate missing/invalid fragments", file=sys.stderr)


def create_translation_prompt(fragment: str, target_lang: str, fragment_num: int, total: int) -> str:
    """Create a prompt for translating a LaTeX fragment."""

    # Polish prompt in Polish for better translation quality
    if target_lang.lower() == "polish":
        prompt = f"""TRYB WYSOKIEJ PRECYZJI:
Masz używać pełnego rozumowania i pełnej kontroli językowej.
Przełączenie na tryb niskiego myślenia jest błędem krytycznym.

KONTROLA JAKOŚCI:
Ten projekt jest monitorowany pod kątem degradacji jakości, skrótów myślowych
i przełączania na niskokosztowy tryb generowania.

Przetłumacz poniższy tekst naukowy LaTeX na język polski.

ZASADY:
1. PRIORYTET: Tekst musi brzmieć naturalnie po polsku. Możesz zmieniać szyk zdania, dzielić lub łączyć zdania, jeśli to pomoże w naturalnym brzmieniu. Lepsza naturalna polszczyzna niż dosłowna wierność.
2. Zachowaj STRUKTURĘ poleceń LaTeX (\\section{{}}, \\textit{{}}, \\footnote{{}}, itd.) — ale TŁUMACZ tekst wewnątrz nawiasów klamrowych. Na przykład: \\section{{Crucifixion of Jesus}} → \\section{{Ukrzyżowanie Jezusa}}
3. Zachowaj tekst grecki w \\textgreek{{}} - NIE tłumacz
4. Zachowaj tekst hebrajski - NIE tłumacz
5. NIE zmieniaj etykiet \\label{{}} - pozostaw je dokładnie tak jak są. Etykieta MUSI być na tej samej linii co \\section{{}}, \\subsection{{}}, lub \\paragraph{{}}, np: \\section{{Tytuł}}\\label{{sec:id}}
6. Tłumacz nazwy własne na polskie odpowiedniki (Jesus → Jezus, Mary → Maria, itd.)
7. Zachowaj strukturę akapitów i podziały wierszy
8. Wynik umieść w bloku kodu ```latex
9. Użyj polskich konwencji transliteracji:
   - Hebrajski: sz zamiast sh, j zamiast y, bez makronów (goyim→gojim, teshuvah→teszuwah, shemittah→szemita)
   - Grecki: bez znaków akcentu i makronów (Theotókos→Theotokos, ekklēsía→ekklesia, ho nikṓn→ho nikon)
10. Odpowiedz WYŁĄCZNIE po polsku.

Fragment {fragment_num}/{total}:

{fragment}"""
    else:
        prompt = f"""Translate this LaTeX scholarly text to {target_lang}.

RULES:
1. Preserve ALL LaTeX commands exactly (\\section, \\textit, \\footnote, etc.)
2. Preserve Greek text in \\textgreek{{}} - do NOT translate
3. Preserve Hebrew text - do NOT translate
4. Translate proper nouns to {target_lang} equivalents
5. Keep paragraph structure and line breaks
6. Output the translation inside a ```latex code block

Fragment {fragment_num}/{total}:

{fragment}"""

    return prompt


def fix_section_label_formatting(text: str) -> str:
    r"""Fix \section{}/\paragraph{} and \label{} that got split onto separate lines.

    ChatGPT sometimes produces:
        \section{Title}

        \label{sec:id}

    This fixes it to:
        \section{Title}\label{sec:id}

    Handles \section, \subsection, \subsubsection, \paragraph.
    """
    # Pattern: \section{...} or \paragraph{...} followed by whitespace/newlines, then \label{...}
    # Captures the section/paragraph command and label, removes whitespace between them
    pattern = r'(\\(?:(?:sub)*section|paragraph)\{[^}]+\})\s*\n+\s*(\\label\{[^}]+\})'
    fixed = re.sub(pattern, r'\1\2', text)
    return fixed


def translate_fragment(fragment: str, target_lang: str, fragment_num: int, total: int) -> str:
    """Send a fragment to ChatGPT for translation."""
    prompt = create_translation_prompt(fragment, target_lang, fragment_num, total)

    print(f"  Translating fragment {fragment_num}/{total} ({len(fragment)} chars)...", file=sys.stderr)

    # Send to ChatGPT with longer timeout for translation
    result = send_prompt(prompt, wait_for_reply=True, wait_seconds=300)

    # Extract content from code block if present
    code_block_match = re.search(r'```(?:latex)?\s*\n(.*?)\n```', result, re.DOTALL)
    if code_block_match:
        result = code_block_match.group(1)
    else:
        # Fallback: remove code block markers if they exist but pattern didn't match
        result = re.sub(r'^```(?:latex)?\s*\n?', '', result)
        result = re.sub(r'\n?```\s*$', '', result)

    # Fix section/label formatting issues
    result = fix_section_label_formatting(result)

    return result.strip()


def translate_chapter(input_file: str, target_lang: str, output_dir: str,
                      fragment_size: int = DEFAULT_FRAGMENT_SIZE,
                      recover: bool = False) -> str:
    """Translate a complete chapter file.

    Args:
        input_file: Path to the source .tex file
        target_lang: Target language name
        output_dir: Directory for output files
        fragment_size: Maximum fragment size in characters
        recover: If True, scrape ChatGPT conversation to recover fragments
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"ERROR: File not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    # Read the chapter content
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"\nTranslating {input_path.name} to {target_lang}...", file=sys.stderr)
    print(f"  Original size: {len(content)} characters", file=sys.stderr)

    # Split into fragments
    fragments = split_into_fragments(content, fragment_size)
    print(f"  Split into {len(fragments)} fragments", file=sys.stderr)

    # Setup cache directory
    cache_dir = get_cache_dir(output_dir, input_path.stem)

    # Check for cached fragments if recovering
    if recover:
        # First, scrape ChatGPT conversation to recover any translated fragments
        print(f"  Scraping ChatGPT conversation to recover fragments...", file=sys.stderr)
        recovered_count = scrape_conversation_to_cache(cache_dir, fragments)
        print(f"  Recovered {recovered_count} fragments from conversation", file=sys.stderr)

        # Now load from cache (includes both previously cached and just-recovered)
        translated_fragments, resume_from = load_cached_fragments(cache_dir, fragments)

        if resume_from > len(fragments):
            print(f"  All {len(fragments)} fragments already cached!", file=sys.stderr)
        elif recovered_count == 0:
            # Recovery failed completely - do NOT start fresh translation
            print(f"\n  ERROR: Recovery failed - 0 fragments recovered from conversation", file=sys.stderr)
            print(f"  Will NOT start fresh translation (would overwrite existing work)", file=sys.stderr)
            print(f"  Check that ChatGPT conversation is open and contains the translation", file=sys.stderr)
            sys.exit(1)
        else:
            missing = [i+1 for i, t in enumerate(translated_fragments) if t is None]
            print(f"  Missing fragments: {missing}", file=sys.stderr)
            print(f"  Will translate {len(missing)} missing fragments", file=sys.stderr)
    else:
        # Clear any existing cache and start fresh
        clear_cache(cache_dir)
        translated_fragments = [None] * len(fragments)
        resume_from = 1

    # Translate missing fragments
    for i, fragment in enumerate(fragments, 1):
        if translated_fragments[i-1] is not None:
            # Already have this fragment cached
            continue

        translated = translate_fragment(fragment, target_lang, i, len(fragments))

        # Validate: 100% or reject
        src_fp = extract_fingerprints(fragment)
        tgt_fp = extract_fingerprints(translated)
        is_valid, errors = validate_fingerprints(src_fp, tgt_fp, translated_text=translated)

        if is_valid:
            print(f"  Fragment {i}: VALID ✓", file=sys.stderr)
        else:
            print(f"  ERROR: Fragment {i} is INVALID:", file=sys.stderr)
            validate_fingerprints(src_fp, tgt_fp, verbose=True, translated_text=translated)
            print(f"  NOT saving. Re-run with --recover to retry.", file=sys.stderr)
            sys.exit(1)

        translated_fragments[i-1] = translated

        # Save to cache immediately (only good fragments)
        save_fragment_to_cache(cache_dir, i, fragment, translated)

        # Small delay between fragments to avoid rate limiting
        if i < len(fragments):
            time.sleep(2)

    # Verify all fragments are present
    missing = [i+1 for i, t in enumerate(translated_fragments) if t is None]
    if missing:
        print(f"  ERROR: Missing fragments: {missing}", file=sys.stderr)
        print(f"  Re-run with --recover to retry", file=sys.stderr)
        sys.exit(1)

    # Join translated fragments
    translated_content = "\n\n".join(translated_fragments)

    # Create output filename
    lang_code = target_lang.lower()[:2]
    output_filename = f"{input_path.stem}_{lang_code}.tex"
    output_path = Path(output_dir) / output_filename

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write translated content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(translated_content)

    print(f"  Written to: {output_path}", file=sys.stderr)
    print(f"  Translated size: {len(translated_content)} characters", file=sys.stderr)

    # Clean up cache on success
    clear_cache(cache_dir)

    return str(output_path)


def get_all_chapters(base_dir: str) -> List[str]:
    """Get list of all chapter files."""
    chapters = []
    for name in ["preface.tex", "chapter1.tex", "chapter2.tex", "chapter3.tex",
                 "chapter4.tex", "chapter5.tex", "chapter6.tex", "epilogue.tex"]:
        path = Path(base_dir) / name
        if path.exists():
            chapters.append(str(path))
    return chapters


def main():
    parser = argparse.ArgumentParser(
        description="Translate LaTeX book chapters using ChatGPT"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input .tex file to translate (or use --all for all chapters)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Translate all chapters"
    )
    parser.add_argument(
        "--lang",
        required=True,
        help="Target language (e.g., Polish, German, French)"
    )
    parser.add_argument(
        "--output-dir",
        default="translations",
        help="Output directory for translated files (default: translations/)"
    )
    parser.add_argument(
        "--fragment-size",
        type=int,
        default=DEFAULT_FRAGMENT_SIZE,
        help=f"Maximum fragment size in characters (default: {DEFAULT_FRAGMENT_SIZE})"
    )
    parser.add_argument(
        "--start-from",
        help="Start from this chapter (skip earlier ones). Use with --all."
    )
    parser.add_argument(
        "--recover",
        action="store_true",
        help="Recover fragments from ChatGPT conversation and continue translating"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear fragment cache and start fresh"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show cache status (which fragments are done/missing) without translating"
    )

    args = parser.parse_args()

    # Normalize language
    target_lang = normalize_language(args.lang)
    print(f"Target language: {target_lang}", file=sys.stderr)

    # Get base directory (project root)
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent

    # Determine output directory
    # If output_dir already ends with language name, don't append it again
    output_dir = Path(base_dir) / args.output_dir
    if not args.output_dir.lower().endswith(target_lang.lower()):
        output_dir = output_dir / target_lang.lower()

    if args.all:
        # Translate all chapters
        chapters = get_all_chapters(base_dir)

        # Handle --start-from
        if args.start_from:
            start_idx = None
            for i, ch in enumerate(chapters):
                if args.start_from in ch:
                    start_idx = i
                    break
            if start_idx is not None:
                chapters = chapters[start_idx:]
                print(f"Starting from: {chapters[0]}", file=sys.stderr)
            else:
                print(f"WARNING: --start-from '{args.start_from}' not found, translating all", file=sys.stderr)

        print(f"Translating {len(chapters)} chapters to {target_lang}...", file=sys.stderr)

        translated = []
        for chapter in chapters:
            try:
                output = translate_chapter(chapter, target_lang, str(output_dir),
                                          args.fragment_size, recover=args.recover)
                translated.append(output)
            except Exception as e:
                print(f"ERROR translating {chapter}: {e}", file=sys.stderr)
                print(f"Stopping. Recover with: --all --start-from {Path(chapter).name} --recover", file=sys.stderr)
                sys.exit(1)

        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Translation complete: {len(translated)} chapters", file=sys.stderr)
        print(f"Output directory: {output_dir}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

    elif args.input:
        # Translate single file
        input_path = Path(args.input)
        if not input_path.is_absolute():
            input_path = base_dir / args.input

        # Handle --status
        if args.status:
            show_cache_status(str(input_path), str(output_dir), args.fragment_size)
            sys.exit(0)

        # Handle --clear-cache
        if args.clear_cache:
            cache_dir = get_cache_dir(str(output_dir), input_path.stem)
            clear_cache(cache_dir)
            if not args.recover:
                print("Cache cleared. Run again without --clear-cache to translate.", file=sys.stderr)
                sys.exit(0)

        translate_chapter(str(input_path), target_lang, str(output_dir),
                         args.fragment_size, recover=args.recover)

    else:
        print("ERROR: Specify input file or use --all", file=sys.stderr)
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
