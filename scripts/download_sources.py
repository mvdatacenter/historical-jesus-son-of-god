#!/usr/bin/env python3
"""
download_sources.py — Download public domain source texts for citation verification.

Downloads ancient and patristic texts from public domain web sources,
strips HTML to plain text, and saves to sources/{category}/{bib_key}/.

Usage:
    poetry run python scripts/download_sources.py                    # Download all
    poetry run python scripts/download_sources.py --category ancient  # Ancient only
    poetry run python scripts/download_sources.py --key josephus:war  # Single source
    poetry run python scripts/download_sources.py --dry-run           # Show what would download
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: poetry add requests beautifulsoup4")
    sys.exit(1)

# Add scripts dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_registry import (
    SOURCES,
    ANCIENT,
    PATRISTIC,
    MODERN,
    get_sources_by_category,
    get_downloadable_sources,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = PROJECT_ROOT / "sources"
REQUEST_DELAY = 3  # Seconds between requests (polite crawling)
MAX_RETRIES = 3    # Number of retry attempts per URL
REQUEST_TIMEOUT = 60  # Seconds

# Common headers to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Minimum acceptable file size (chars) — below this, treat as stub/redirect
MIN_TEXT_SIZE = {
    "newadvent.org": 500,       # New Advent pages should be substantial
    "perseus.tufts.edu": 500,   # Perseus pages should have actual text
    "gutenberg.org": 1000,      # Gutenberg pages should be very substantial
    "earlychristianwritings.com": 500,  # ECW pages should have actual text
    "default": 100,
}


def clean_html_to_text(html_content, url=""):
    """Extract readable text from HTML, removing navigation, scripts, etc."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script, style, nav elements
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()

    # For Perseus, find the main text div
    if "perseus.tufts.edu" in url:
        text_div = soup.find("div", class_="text_container")
        if not text_div:
            text_div = soup.find("div", id="text_container")
        if text_div:
            soup = text_div

    # For New Advent, find the main content
    elif "newadvent.org" in url:
        # New Advent uses various structures. Try multiple selectors:
        content = None
        # Try <div class="entry-content"> (newer pages)
        content = soup.find("div", class_="entry-content")
        if not content:
            # Try the body element directly — strip nav/sidebar
            body = soup.find("body")
            if body:
                # Remove navigation, sidebar, footer elements
                for tag in body(["nav", "header", "footer", "aside",
                                 "script", "style"]):
                    tag.decompose()
                # Remove common nav/menu divs
                for div in body.find_all("div", class_=re.compile(
                        r"nav|menu|sidebar|footer|header", re.I)):
                    div.decompose()
                content = body
        if content:
            soup = content

    # For LacusCurtius, find the text body
    elif "penelope.uchicago.edu" in url:
        content = soup.find("div", class_="text")
        if not content:
            content = soup.find("td", class_="text")
        if content:
            soup = content

    # For Early Jewish Writings — full text is in the body, not a specific div
    elif "earlyjewishwritings.com" in url:
        body = soup.find("body")
        if body:
            for tag in body(["nav", "header", "footer", "script", "style"]):
                tag.decompose()
            soup = body

    # For Early Christian Writings — text is in div#infolayer or body
    elif "earlychristianwritings.com" in url:
        content = soup.find("div", id="infolayer")
        if not content:
            body = soup.find("body")
            if body:
                for tag in body(["nav", "header", "footer", "script", "style"]):
                    tag.decompose()
                content = body
        if content:
            soup = content

    # For tertullian.org — text is in body, strip navigation
    elif "tertullian.org" in url:
        # tertullian.org sometimes has malformed tags (e.g. </style without >)
        # which causes html.parser to fail. Re-parse if body not found.
        body = soup.find("body")
        if not body:
            import re as _re
            fixed_html = _re.sub(r'</style(?!\s*>)', '</style>', html_content, flags=_re.I)
            soup = BeautifulSoup(fixed_html, "html.parser")
            body = soup.find("body")
        if body:
            for tag in body(["nav", "header", "footer", "script", "style"]):
                tag.decompose()
            soup = body

    # For Project Gutenberg — text is in body, strip nav
    elif "gutenberg.org" in url:
        body = soup.find("body")
        if body:
            for tag in body(["nav", "header", "footer", "script", "style"]):
                tag.decompose()
            soup = body

    # For Attalus.org — text is in body
    elif "attalus.org" in url:
        body = soup.find("body")
        if body:
            for tag in body(["nav", "header", "footer", "script", "style"]):
                tag.decompose()
            soup = body

    # Get text and clean up
    text = soup.get_text(separator="\n")

    # Clean up whitespace
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if line:
            lines.append(line)

    text = "\n".join(lines)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _get_min_size(url):
    """Get the minimum acceptable text size for a given URL's domain."""
    for domain, size in MIN_TEXT_SIZE.items():
        if domain in url:
            return size
    return MIN_TEXT_SIZE["default"]


def download_url(url, dest_path, dry_run=False):
    """Download a single URL and save as plain text. Returns True on success."""
    min_size = _get_min_size(url)

    if dest_path.exists() and dest_path.stat().st_size > min_size:
        print(f"  SKIP (exists): {dest_path.name}")
        return True

    if dry_run:
        print(f"  WOULD DOWNLOAD: {url}")
        print(f"    -> {dest_path}")
        return True

    # Plain text URLs (e.g., archive.org DjVu text) — save directly
    is_plain_text = url.endswith(".txt")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if attempt > 1:
                wait = REQUEST_DELAY * attempt
                print(f"  Retry {attempt}/{MAX_RETRIES} (waiting {wait}s)...")
                time.sleep(wait)

            print(f"  Downloading: {url}")
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()

            if is_plain_text:
                text = resp.text.strip()
            else:
                text = clean_html_to_text(resp.text, url)

            if len(text) < min_size:
                print(f"  WARNING: Very short text ({len(text)} chars) — "
                      f"below {min_size} char minimum for this source")
                if attempt < MAX_RETRIES:
                    continue  # Retry — might be a partial response
                return False

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(text, encoding="utf-8")
            print(f"  SAVED: {dest_path.name} ({len(text):,} chars)")
            return True

        except requests.RequestException as e:
            print(f"  ERROR: {e}")
            if attempt < MAX_RETRIES:
                continue
            return False

    return False


def download_source(key, source_info, dry_run=False):
    """Download all URLs for a single bibliography entry."""
    category = source_info["category"]
    urls = source_info.get("urls", {})

    if not urls:
        if source_info.get("note"):
            print(f"  NOTE: {source_info['note']}")
        else:
            print(f"  No URLs available")
        return 0, 0

    dest_dir = SOURCES_DIR / category / key.replace(":", "_")

    success = 0
    total = 0

    for section_name, url in urls.items():
        total += 1
        safe_name = re.sub(r"[^\w\-]", "_", section_name)
        dest_path = dest_dir / f"{safe_name}.txt"

        if download_url(url, dest_path, dry_run):
            success += 1

        if not dry_run and total < len(urls):
            time.sleep(REQUEST_DELAY)

    return success, total


def print_modern_instructions():
    """Print instructions for obtaining modern copyrighted works."""
    modern = get_sources_by_category(MODERN)
    print("\n" + "=" * 70)
    print("MODERN WORKS — Copyrighted (not downloaded)")
    print("=" * 70)
    print(f"See sources/modern/README.md for detailed instructions.")
    print(f"{len(modern)} modern works registered:")
    for key, info in modern.items():
        print(f"  - {key}: {info['title']} ({info.get('year', 'n.d.')})")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Download public domain source texts for citation verification."
    )
    parser.add_argument(
        "--category",
        choices=["ancient", "patristic", "all"],
        default="all",
        help="Category to download (default: all)",
    )
    parser.add_argument(
        "--key",
        type=str,
        help="Download a single source by bib key (e.g., josephus:war)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without downloading",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("Source Text Downloader")
    print("=" * 70)

    if args.key:
        # Single source
        if args.key not in SOURCES:
            print(f"ERROR: Unknown key '{args.key}'")
            print(f"Available keys: {', '.join(sorted(SOURCES.keys()))}")
            sys.exit(1)

        info = SOURCES[args.key]
        if info["category"] == MODERN:
            print(f"\n'{args.key}' is a modern (copyrighted) work.")
            print(f"  Obtain: {info.get('obtain', 'See sources/modern/README.md')}")
            return

        print(f"\nDownloading: {args.key} — {info['title']}")
        success, total = download_source(args.key, info, args.dry_run)
        print(f"\nResult: {success}/{total} files downloaded")
        return

    # Category-based download
    total_success = 0
    total_count = 0

    if args.category in ("ancient", "all"):
        ancient = get_sources_by_category(ANCIENT)
        print(f"\n--- ANCIENT SOURCES ({len(ancient)} entries) ---\n")
        for key, info in ancient.items():
            print(f"\n[{key}] {info['title']}")
            s, t = download_source(key, info, args.dry_run)
            total_success += s
            total_count += t
            if not args.dry_run and t > 0:
                time.sleep(REQUEST_DELAY)

    if args.category in ("patristic", "all"):
        patristic = get_sources_by_category(PATRISTIC)
        print(f"\n--- PATRISTIC SOURCES ({len(patristic)} entries) ---\n")
        for key, info in patristic.items():
            print(f"\n[{key}] {info['title']}")
            s, t = download_source(key, info, args.dry_run)
            total_success += s
            total_count += t
            if not args.dry_run and t > 0:
                time.sleep(REQUEST_DELAY)

    print_modern_instructions()

    print("=" * 70)
    print(f"TOTAL: {total_success}/{total_count} files downloaded successfully")
    if args.dry_run:
        print("(dry run — nothing was actually downloaded)")
    print("=" * 70)


if __name__ == "__main__":
    main()
