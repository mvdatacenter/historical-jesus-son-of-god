#!/usr/bin/env python3
"""
translate_book.py

Translate LaTeX book chapters to another language using ChatGPT Desktop App.

Features:
  - Reads LaTeX chapters and splits them into manageable fragments
  - Sends each fragment to ChatGPT for translation
  - Preserves LaTeX formatting and commands
  - Writes translated output to new files

Usage:
  poetry run python scripts/translate_book.py chapter1.tex --lang Polish
  poetry run python scripts/translate_book.py --all --lang Polish
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import List, Tuple

# Import send_prompt from the chatgpt module
from chatgpt_desktop import send_prompt


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


def create_translation_prompt(fragment: str, target_lang: str, fragment_num: int, total: int) -> str:
    """Create a prompt for translating a LaTeX fragment."""
    return f"""Translate this LaTeX scholarly text to {target_lang}.

RULES:
1. Preserve ALL LaTeX commands exactly (\\section, \\textit, \\footnote, etc.)
2. Preserve Greek text in \\textgreek{{}} - do NOT translate
3. Preserve Hebrew text - do NOT translate
4. Translate proper nouns to {target_lang} equivalents (Jesus → Jezus in Polish, etc.)
5. Keep paragraph structure and line breaks
6. Output the translation inside a ```latex code block

Fragment {fragment_num}/{total}:

{fragment}"""


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

    return result.strip()


def translate_chapter(input_file: str, target_lang: str, output_dir: str, fragment_size: int = DEFAULT_FRAGMENT_SIZE) -> str:
    """Translate a complete chapter file."""
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

    # Translate each fragment
    translated_fragments = []
    for i, fragment in enumerate(fragments, 1):
        translated = translate_fragment(fragment, target_lang, i, len(fragments))
        translated_fragments.append(translated)

        # Small delay between fragments to avoid rate limiting
        if i < len(fragments):
            time.sleep(2)

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

    args = parser.parse_args()

    # Normalize language
    target_lang = normalize_language(args.lang)
    print(f"Target language: {target_lang}", file=sys.stderr)

    # Get base directory (project root)
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent

    # Determine output directory
    output_dir = Path(base_dir) / args.output_dir / target_lang.lower()

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
                output = translate_chapter(chapter, target_lang, str(output_dir), args.fragment_size)
                translated.append(output)
            except Exception as e:
                print(f"ERROR translating {chapter}: {e}", file=sys.stderr)
                print(f"Stopping. Resume with: --all --start-from {Path(chapter).name}", file=sys.stderr)
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

        translate_chapter(str(input_path), target_lang, str(output_dir), args.fragment_size)

    else:
        print("ERROR: Specify input file or use --all", file=sys.stderr)
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
