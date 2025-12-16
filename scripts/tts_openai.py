#!/usr/bin/env python3
"""
Text-to-Speech using OpenAI API.

Usage:
    poetry run python scripts/tts_openai.py chapter1.tex --output audiobook/chapter1.mp3
    poetry run python scripts/tts_openai.py chapter1.tex --voice nova --model tts-1-hd

Large chapters (>50K chars) are automatically split into parts and processed in parallel.
Part files are deleted after combining (use --keep-parts to preserve them).

Options:
    --output, -o    Output MP3 file path
    --voice, -v     Voice to use (default: nova)
    --model, -m     Model to use (default: tts-1)
    --dry-run       Show text preview and cost estimate without calling API
    --list-parts    Show how the chapter would be split
    --part N        Generate only part N (for manual parallel processing)
    --combine       Combine existing part files into final output
    --keep-parts    Keep part files after combining (default: delete them)

Voices: alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse
Models: tts-1 (faster, cheaper), tts-1-hd (higher quality), gpt-4o-mini-tts (newest)
"""

import argparse
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
import httpx

# Import shared utilities
from text_utils import split_into_fragments, split_into_tts_chunks, strip_latex

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

# Max chars for a single TTS request
TTS_CHUNK_SIZE = 4000

# Max chars before we split a chapter into multiple audio files
# (to avoid rate limits and provide progress)
CHAPTER_SPLIT_SIZE = 50000


def load_api_key() -> str:
    """Load OpenAI API key from environment (loaded from .env)."""
    if key := os.environ.get("OPENAI_API_KEY"):
        return key

    raise RuntimeError(
        "No OpenAI API key found. Create .env file with OPENAI_API_KEY=your-key"
    )


def generate_speech(
    text: str,
    output_path: Path,
    voice: str = "nova",
    model: str = "tts-1",
    client: OpenAI = None,
    max_retries: int = 3,
) -> None:
    """Generate speech from text and save to file with retry logic."""
    if client is None:
        client = OpenAI(
            api_key=load_api_key(),
            timeout=httpx.Timeout(300.0, connect=30.0),
        )

    for attempt in range(max_retries):
        try:
            with client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=text,
            ) as response:
                response.stream_to_file(str(output_path))
            return  # Success
        except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt * 5  # 5s, 10s, 20s
                print(f"    Timeout, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise


def generate_chapter_audio(
    plain_text: str,
    output_path: Path,
    voice: str,
    model: str,
    client: OpenAI,
    part_num: int = None,
    total_parts: int = None,
) -> None:
    """Generate audio for a chapter, handling chunking and concatenation."""
    # Split into TTS-sized chunks (max 4096 chars each)
    chunks = split_into_tts_chunks(plain_text, TTS_CHUNK_SIZE)
    prefix = f"[Part {part_num}/{total_parts}] " if part_num else ""
    print(f"{prefix}Generating {len(chunks)} audio chunk(s)...")

    if len(chunks) == 1:
        generate_speech(chunks[0], output_path, voice, model, client)
        print(f"{prefix}Saved: {output_path}")
    else:
        # Generate chunks to temp files and concatenate
        temp_files = []

        for i, chunk in enumerate(chunks, 1):
            temp_path = Path(tempfile.mktemp(suffix=".mp3"))
            temp_files.append(temp_path)
            print(f"{prefix}  Chunk {i}/{len(chunks)}: {len(chunk)} chars")
            generate_speech(chunk, temp_path, voice, model, client)

        # Concatenate all chunks into single file
        print(f"{prefix}Combining {len(temp_files)} chunks...")
        with open(output_path, "wb") as outfile:
            for temp_path in temp_files:
                outfile.write(temp_path.read_bytes())
                temp_path.unlink()  # Clean up temp file

        print(f"{prefix}Saved: {output_path}")


def generate_part(
    part_num: int,
    fragment: str,
    output_path: Path,
    voice: str,
    model: str,
    total_parts: int,
) -> tuple[int, Path, Exception | None]:
    """Generate a single part (for parallel execution). Returns (part_num, path, error)."""
    part_path = output_path.with_stem(f"{output_path.stem}_part{part_num:02d}")
    try:
        # Each thread gets its own client
        client = OpenAI(
            api_key=load_api_key(),
            timeout=httpx.Timeout(300.0, connect=30.0),
        )
        generate_chapter_audio(fragment, part_path, voice, model, client, part_num, total_parts)
        return (part_num, part_path, None)
    except Exception as e:
        print(f"[Part {part_num}/{total_parts}] FAILED: {e}")
        return (part_num, part_path, e)


def main():
    parser = argparse.ArgumentParser(description="Convert LaTeX chapter to speech")
    parser.add_argument("input", help="Input LaTeX file")
    parser.add_argument("--output", "-o", help="Output MP3 file")
    parser.add_argument("--voice", "-v", default="nova",
                       choices=["alloy", "ash", "ballad", "coral", "echo",
                                "fable", "nova", "onyx", "sage", "shimmer", "verse"],
                       help="Voice to use (default: nova)")
    parser.add_argument("--model", "-m", default="tts-1",
                       choices=["tts-1", "tts-1-hd", "gpt-4o-mini-tts"],
                       help="Model to use (default: tts-1)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show text that would be converted without calling API")
    parser.add_argument("--part", type=int, metavar="N",
                       help="Generate only part N (1-indexed) for parallel processing")
    parser.add_argument("--combine", action="store_true",
                       help="Combine existing part files into final output")
    parser.add_argument("--list-parts", action="store_true",
                       help="Show how the chapter would be split into parts")
    parser.add_argument("--keep-parts", action="store_true",
                       help="Keep part files after combining (default: delete them)")

    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        # Try in project root
        input_path = Path(__file__).parent.parent / args.input

    if not input_path.exists():
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    latex_text = input_path.read_text()
    plain_text = strip_latex(latex_text)

    print(f"Input: {input_path.name}")
    print(f"Original: {len(latex_text):,} chars")
    print(f"Plain text: {len(plain_text):,} chars")

    # Split into parts for parallel processing
    fragments = split_into_fragments(plain_text, CHAPTER_SPLIT_SIZE)
    num_parts = len(fragments)

    if args.list_parts:
        print(f"\nChapter splits into {num_parts} parts:")
        for i, frag in enumerate(fragments, 1):
            chunks = split_into_tts_chunks(frag, TTS_CHUNK_SIZE)
            print(f"  Part {i}: {len(frag):,} chars -> {len(chunks)} TTS chunks")
        print(f"\nTo generate in parallel:")
        for i in range(1, num_parts + 1):
            print(f"  poetry run python scripts/tts_openai.py {args.input} --part {i} &")
        print(f"  wait")
        print(f"  poetry run python scripts/tts_openai.py {args.input} --combine")
        return

    if args.dry_run:
        print("\n--- Preview (first 2000 chars) ---")
        print(plain_text[:2000])
        print("\n--- End preview ---")

        chunks = split_into_tts_chunks(plain_text, TTS_CHUNK_SIZE)
        print(f"\nWould generate {len(chunks)} audio chunks across {num_parts} parts")

        # Estimate cost
        cost = len(plain_text) / 1_000_000 * 15  # $15/1M chars for tts-1
        if args.model == "tts-1-hd":
            cost *= 2  # tts-1-hd is $30/1M
        print(f"Estimated cost: ${cost:.4f}")
        return

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path(__file__).parent.parent / "audiobook"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{input_path.stem}.mp3"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle --combine: just merge existing part files
    if args.combine:
        print(f"Combining {num_parts} parts into {output_path}...")
        with open(output_path, "wb") as outfile:
            for i in range(1, num_parts + 1):
                part_path = output_path.with_stem(f"{output_path.stem}_part{i:02d}")
                if not part_path.exists():
                    print(f"  Missing: {part_path}")
                    sys.exit(1)
                size_mb = part_path.stat().st_size / 1024 / 1024
                print(f"  + Part {i}: {part_path.name} ({size_mb:.1f} MB)")
                outfile.write(part_path.read_bytes())
        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"Final: {output_path} ({size_mb:.1f} MB)")
        return

    client = OpenAI(
        api_key=load_api_key(),
        timeout=httpx.Timeout(300.0, connect=30.0),  # 5 min read, 30s connect
    )

    # Handle --part: generate only a specific part
    if args.part:
        if args.part < 1 or args.part > num_parts:
            print(f"Error: Part {args.part} out of range (1-{num_parts})")
            sys.exit(1)
        part_path = output_path.with_stem(f"{output_path.stem}_part{args.part:02d}")
        fragment = fragments[args.part - 1]
        print(f"=== Generating Part {args.part}/{num_parts} ({len(fragment):,} chars) ===")
        generate_chapter_audio(fragment, part_path, args.voice, args.model, client)
        return

    # Default: generate all parts in parallel, then combine
    if num_parts > 1:
        print(f"Large chapter: splitting into {num_parts} parts (parallel execution)")
        for i, frag in enumerate(fragments, 1):
            chunks = split_into_tts_chunks(frag, TTS_CHUNK_SIZE)
            print(f"  Part {i}: {len(frag):,} chars -> {len(chunks)} chunks")

        # Run parts in parallel
        failed_parts = []
        with ThreadPoolExecutor(max_workers=num_parts) as executor:
            futures = {
                executor.submit(
                    generate_part, i, frag, output_path, args.voice, args.model, num_parts
                ): i
                for i, frag in enumerate(fragments, 1)
            }

            for future in as_completed(futures):
                part_num, part_path, error = future.result()
                if error:
                    failed_parts.append((part_num, error))

        if failed_parts:
            print(f"\nFAILED parts: {[p[0] for p in failed_parts]}")
            for part_num, error in failed_parts:
                print(f"  Part {part_num}: {error}")
            sys.exit(1)

        # Combine all parts
        print(f"\nCombining all parts into {output_path}...")
        part_paths = []
        with open(output_path, "wb") as outfile:
            for i in range(1, num_parts + 1):
                part_path = output_path.with_stem(f"{output_path.stem}_part{i:02d}")
                part_paths.append(part_path)
                size_mb = part_path.stat().st_size / 1024 / 1024
                print(f"  + Part {i}: {size_mb:.1f} MB")
                outfile.write(part_path.read_bytes())

        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"Final: {output_path} ({size_mb:.1f} MB)")

        # Clean up part files (unless --keep-parts)
        if not args.keep_parts:
            for part_path in part_paths:
                part_path.unlink()
            print(f"Cleaned up {len(part_paths)} part files")
    else:
        generate_chapter_audio(plain_text, output_path, args.voice, args.model, client)


if __name__ == "__main__":
    main()
