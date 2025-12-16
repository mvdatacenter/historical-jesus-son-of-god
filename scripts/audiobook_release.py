#!/usr/bin/env python3
"""
Merge audiobook chapters and upload to GitHub Releases.

Usage:
    poetry run python scripts/audiobook_release.py --merge
    poetry run python scripts/audiobook_release.py --upload v1.0.0
    poetry run python scripts/audiobook_release.py --all v1.0.0
"""

import argparse
import subprocess
import sys
from pathlib import Path


AUDIOBOOK_DIR = Path(__file__).parent.parent / "audiobook"
POLISH_FILES = [
    "00_przedmowa_pl.mp3",
    "01_rozdzial_1.mp3",
    "02_rozdzial_2.mp3",
    "03_rozdzial_3.mp3",
    "04_rozdzial_4.mp3",
    "05_rozdzial_5.mp3",
    "06_rozdzial_6.mp3",
    "07_epilog_pl.mp3",
]


def merge_audiobook(lang: str = "polish") -> Path:
    """Merge all chapter MP3s into a single file."""
    if lang == "polish":
        files = POLISH_FILES
        output = AUDIOBOOK_DIR / "audiobook_polish.mp3"
    else:
        raise ValueError(f"Unsupported language: {lang}")

    # Check all files exist
    missing = []
    for f in files:
        if not (AUDIOBOOK_DIR / f).exists():
            missing.append(f)

    if missing:
        print(f"Missing files: {missing}")
        sys.exit(1)

    # Simple concatenation (MP3s can be concatenated directly)
    print(f"Merging {len(files)} files into {output.name}...")
    with open(output, "wb") as outfile:
        for f in files:
            filepath = AUDIOBOOK_DIR / f
            print(f"  + {f} ({filepath.stat().st_size / 1024 / 1024:.1f} MB)")
            outfile.write(filepath.read_bytes())

    size_mb = output.stat().st_size / 1024 / 1024
    print(f"Created: {output} ({size_mb:.1f} MB)")
    return output


def upload_to_release(tag: str, files: list[Path]) -> None:
    """Upload files to a GitHub release."""
    # Check if release exists, create if not
    result = subprocess.run(
        ["gh", "release", "view", tag],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Creating release {tag}...")
        subprocess.run(
            ["gh", "release", "create", tag,
             "--title", f"Audiobook {tag}",
             "--notes", "Polish audiobook generated with OpenAI TTS"],
            check=True,
        )

    # Upload files
    for f in files:
        print(f"Uploading {f.name}...")
        subprocess.run(
            ["gh", "release", "upload", tag, str(f), "--clobber"],
            check=True,
        )

    print(f"Done! View at: gh release view {tag}")


def main():
    parser = argparse.ArgumentParser(description="Merge and upload audiobook")
    parser.add_argument("--merge", action="store_true", help="Merge chapter files")
    parser.add_argument("--upload", metavar="TAG", help="Upload to GitHub release")
    parser.add_argument("--all", metavar="TAG", help="Merge and upload")
    parser.add_argument("--lang", default="polish", help="Language (default: polish)")
    parser.add_argument("--chapters", action="store_true",
                       help="Also upload individual chapter files")

    args = parser.parse_args()

    if args.all:
        merged = merge_audiobook(args.lang)
        files = [merged]
        if args.chapters:
            if args.lang == "polish":
                files.extend(AUDIOBOOK_DIR / f for f in POLISH_FILES
                           if (AUDIOBOOK_DIR / f).exists())
        upload_to_release(args.all, files)
    elif args.merge:
        merge_audiobook(args.lang)
    elif args.upload:
        merged = AUDIOBOOK_DIR / f"audiobook_{args.lang}.mp3"
        if not merged.exists():
            print(f"Merged file not found: {merged}")
            print("Run with --merge first")
            sys.exit(1)
        files = [merged]
        if args.chapters:
            if args.lang == "polish":
                files.extend(AUDIOBOOK_DIR / f for f in POLISH_FILES
                           if (AUDIOBOOK_DIR / f).exists())
        upload_to_release(args.upload, files)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
