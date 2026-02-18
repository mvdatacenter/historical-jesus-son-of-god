#!/usr/bin/env python3
"""
download_ia_authenticated.py — Download printdisabled texts from Archive.org.

Handles books in the "printdisabled" collection that require authentication.
Uses Archive.org's lending system: borrow -> extract OCR text -> return.

Usage:
    poetry run python scripts/download_ia_authenticated.py              # Download all
    poetry run python scripts/download_ia_authenticated.py --key KEY    # Single source
    poetry run python scripts/download_ia_authenticated.py --dry-run    # Show what would download
    poetry run python scripts/download_ia_authenticated.py --list       # List available items

Credentials:
    Set IA_EMAIL and IA_PASSWORD in .env file (project root).
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

try:
    import requests
except ImportError:
    print("Missing requests. Run: poetry add requests")
    sys.exit(1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_registry import SOURCES, MODERN

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env file if present
_env_path = PROJECT_ROOT / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SOURCES_DIR = PROJECT_ROOT / "sources"
PAGE_DELAY = 0.5       # Seconds between page requests
REQUEST_TIMEOUT = 30    # Per-request timeout
BOOK_DELAY = 5          # Seconds between books

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Archive.org printdisabled items: bib_key -> archive_org_identifier
IA_PRINTDISABLED = {
    "brandon:zealots": "jesuszealotsstud00bran",
    "brandon:fall": "fallofjerusalemc0000bran",
    "thiering:jesusman": "jesusmandecoding0000thie",
    "jacobovici:tomb": "jesusfamilytombt00jaco",
    "assmann:searchgod": "searchforgodinan0000assm",
    "dodd:fourthgospel": "interpretationof0000dodd_p7r5",
    "brown:johannine": "communityofbelo00raym",
    "boyarin:jewishgospels": "jewishgospelssto0000boya",
    "esler:galatians": "galatians0000esle",
    "hengel:fourgospels": "fourgospelsonego0000heng",
    "johnson:writings": "writingsofnewtes0000john",
    "borgen:philo": "gospelofjohnmore0000borg",
}


def ia_login(email, password):
    """Log into Archive.org using the token-based API and return session."""
    session = requests.Session()
    session.headers.update(HEADERS)

    print("Logging into Archive.org...")

    # Step 1: Get login token
    resp = session.get(
        "https://archive.org/services/account/login/",
        timeout=REQUEST_TIMEOUT,
    )
    try:
        token_data = resp.json()
        token = token_data.get("value", {}).get("token", "")
    except (json.JSONDecodeError, KeyError):
        token = ""

    if not token:
        # Fallback: try form-based login
        resp = session.post(
            "https://archive.org/account/login",
            data={"username": email, "password": password, "action": "login"},
            timeout=REQUEST_TIMEOUT,
        )
    else:
        # Step 2: Submit credentials with token
        resp = session.post(
            "https://archive.org/services/account/login/",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=json.dumps({"username": email, "password": password, "t": token}),
            timeout=REQUEST_TIMEOUT,
        )

    # Verify login
    cookies = {c.name: c.value for c in session.cookies}
    if "logged-in-sig" in cookies and "logged-in-user" in cookies:
        print(f"  Logged in as: {cookies['logged-in-user']}")
        return session

    # Alternative: check account page
    resp2 = session.get(
        "https://archive.org/account/", timeout=REQUEST_TIMEOUT, allow_redirects=False
    )
    if resp2.status_code == 200:
        print("  Login successful (verified via account page).")
        return session

    print("  ERROR: Login failed. Check credentials in .env file.")
    return None


def get_book_metadata(session, identifier):
    """Get book metadata: page count, server, and directory path."""
    url = f"https://archive.org/metadata/{identifier}"
    resp = session.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    meta = data.get("metadata", {})
    page_count = int(meta.get("imagecount", 0))
    server = data.get("server", "")
    dir_path = data.get("dir", "")

    return {
        "title": meta.get("title", "Unknown"),
        "pages": page_count,
        "server": server,
        "dir": dir_path,
        "identifier": identifier,
    }


def borrow_book(session, identifier):
    """Borrow a book via Archive.org's lending API. Returns True on success."""
    print(f"  Borrowing {identifier}...")

    # Step 1: Grant search-inside access
    try:
        session.post(
            "https://archive.org/services/loans/loan/searchInside.php",
            data={"action": "grant_access", "identifier": identifier},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        pass  # Not critical if this fails

    # Step 2: Browse book (initiates lending)
    try:
        resp = session.post(
            "https://archive.org/services/loans/loan/",
            data={"action": "browse_book", "identifier": identifier},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            print(f"  WARNING: browse_book returned {resp.status_code}")
    except requests.RequestException as e:
        print(f"  WARNING: browse_book failed: {e}")

    # Step 3: Create access token
    try:
        resp = session.post(
            "https://archive.org/services/loans/loan/",
            data={"action": "create_token", "identifier": identifier},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code == 200:
            print("  Borrowed successfully.")
            return True
        else:
            print(f"  WARNING: create_token returned {resp.status_code}")
            # Try anyway — sometimes the book is already borrowed
            return True
    except requests.RequestException as e:
        print(f"  ERROR borrowing: {e}")
        return False


def return_book(session, identifier):
    """Return a borrowed book."""
    try:
        resp = session.post(
            "https://archive.org/services/loans/loan/",
            data={"action": "return_loan", "identifier": identifier},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code == 200:
            print(f"  Returned {identifier}.")
        else:
            print(f"  WARNING: return_loan status {resp.status_code}")
    except requests.RequestException as e:
        print(f"  WARNING: Could not return book: {e}")


def fetch_page_text(session, server, dir_path, identifier, page_num):
    """Fetch OCR text for a single page via BookReaderGetTextWrapper."""
    url = (
        f"https://{server}/BookReader/BookReaderGetTextWrapper.php"
        f"?path={dir_path}/{identifier}_djvu.xml&page={page_num}"
    )
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return None

        text = resp.text.strip()

        # Check for HTML error pages
        if text.startswith("<!DOCTYPE") or text.startswith("<html"):
            return None

        # Response format: br.ttsStartCB([["text", [coords], ...], ...])
        # Extract the JSON array from the JSONP wrapper
        if text.startswith("br.ttsStartCB("):
            json_str = text[len("br.ttsStartCB("):]
            if json_str.endswith(")"):
                json_str = json_str[:-1]
            try:
                data = json.loads(json_str)
                if isinstance(data, list):
                    paragraphs = []
                    for item in data:
                        if isinstance(item, list) and len(item) > 0 and isinstance(item[0], str):
                            paragraphs.append(item[0])
                    return "\n".join(paragraphs)
            except json.JSONDecodeError:
                pass

        # Fallback: try plain JSON
        try:
            data = json.loads(text)
            if isinstance(data, list):
                paragraphs = []
                for item in data:
                    if isinstance(item, list) and len(item) > 0 and isinstance(item[0], str):
                        paragraphs.append(item[0])
                    elif isinstance(item, str):
                        paragraphs.append(item)
                return "\n".join(paragraphs)
        except json.JSONDecodeError:
            pass

        # Fallback: strip HTML tags if present
        if "<" in text:
            clean = re.sub(r"<[^>]+>", " ", text)
            clean = re.sub(r"\s+", " ", clean).strip()
            if clean:
                return clean

        return text if text else None

    except requests.RequestException:
        return None


def download_book_text(session, identifier, dest_path, dry_run=False):
    """Download full book text via BookReader page-by-page OCR extraction."""

    if dest_path.exists() and dest_path.stat().st_size > 1000:
        print(f"  SKIP (exists): {dest_path.name} ({dest_path.stat().st_size:,} bytes)")
        return True

    # Get metadata
    try:
        meta = get_book_metadata(session, identifier)
    except requests.RequestException as e:
        print(f"  ERROR getting metadata: {e}")
        return False

    print(f"  Title: {meta['title']}")
    print(f"  Pages: {meta['pages']}")
    print(f"  Server: {meta['server']}")

    if meta["pages"] == 0:
        print("  ERROR: No pages found.")
        return False

    if dry_run:
        print(f"  WOULD DOWNLOAD: {meta['pages']} pages from {meta['server']}")
        print(f"    -> {dest_path}")
        return True

    # Borrow the book
    if not borrow_book(session, identifier):
        print("  ERROR: Could not borrow book.")
        return False

    # Give the loan a moment to activate
    time.sleep(2)

    # Fetch text page by page
    all_pages = []
    errors = 0
    empty = 0

    for page_num in range(meta["pages"]):
        text = fetch_page_text(
            session, meta["server"], meta["dir"], identifier, page_num
        )

        if text is None:
            errors += 1
            if errors <= 3:
                print(f"  Page {page_num}: ERROR (will retry)")
            elif errors == 4:
                print(f"  (suppressing further error messages...)")
        elif len(text.strip()) < 5:
            empty += 1
        else:
            all_pages.append(text)

        # Progress every 50 pages
        if (page_num + 1) % 50 == 0:
            print(
                f"  Progress: {page_num + 1}/{meta['pages']} pages "
                f"({len(all_pages)} with text, {errors} errors, {empty} empty)"
            )

        time.sleep(PAGE_DELAY)

    # Return the book
    return_book(session, identifier)

    # Check results
    total_text = "\n\n".join(all_pages)
    print(
        f"  Result: {len(all_pages)} pages with text, "
        f"{errors} errors, {empty} empty pages"
    )
    print(f"  Total text: {len(total_text):,} chars")

    if len(total_text) < 1000:
        print("  ERROR: Too little text extracted. The borrowing may have failed.")
        return False

    # Save
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(total_text, encoding="utf-8")
    print(f"  SAVED: {dest_path.name} ({len(total_text):,} chars)")
    return True


def get_credentials():
    """Get Archive.org credentials from .env file."""
    email = os.environ.get("IA_EMAIL")
    password = os.environ.get("IA_PASSWORD")

    if email and password:
        print(f"Using credentials from .env (IA_EMAIL={email})")
        return email, password

    print("ERROR: Set IA_EMAIL and IA_PASSWORD in .env file at project root.")
    print("Example .env contents:")
    print("  IA_EMAIL=you@example.com")
    print("  IA_PASSWORD=yourpassword")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Download printdisabled texts from Archive.org via lending API."
    )
    parser.add_argument(
        "--key", type=str,
        help="Download a single source by bib key",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be downloaded",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available printdisabled items and exit",
    )
    args = parser.parse_args()

    # List mode
    if args.list:
        print(f"\n{len(IA_PRINTDISABLED)} printdisabled items available:\n")
        for key, ia_id in sorted(IA_PRINTDISABLED.items()):
            info = SOURCES.get(key, {})
            title = info.get("title", "?")
            author = info.get("author", "?")
            safe_key = key.replace(":", "_")
            dest = SOURCES_DIR / "modern" / safe_key / "full.txt"
            status = "DOWNLOADED" if dest.exists() else "PENDING"
            print(f"  [{status:10s}] {key:25s} {author} — {title}")
        return

    # Validate key if provided
    if args.key:
        if args.key not in IA_PRINTDISABLED:
            print(f"ERROR: '{args.key}' is not a printdisabled item.")
            print(f"Available: {', '.join(sorted(IA_PRINTDISABLED.keys()))}")
            sys.exit(1)
        items = {args.key: IA_PRINTDISABLED[args.key]}
    else:
        items = IA_PRINTDISABLED

    # Get credentials and log in
    email, password = get_credentials()
    session = ia_login(email, password)
    if not session:
        sys.exit(1)

    # Download
    print(f"\n{'=' * 70}")
    print(f"Downloading {len(items)} printdisabled item(s) via lending API")
    print(f"{'=' * 70}\n")

    success = 0
    total = 0
    for key, ia_id in sorted(items.items()):
        total += 1
        info = SOURCES.get(key, {})
        title = info.get("title", "?")
        print(f"\n[{key}] {title}")

        safe_key = key.replace(":", "_")
        dest_path = SOURCES_DIR / "modern" / safe_key / "full.txt"

        if download_book_text(session, ia_id, dest_path, args.dry_run):
            success += 1

        if not args.dry_run and total < len(items):
            time.sleep(BOOK_DELAY)

    print(f"\n{'=' * 70}")
    print(f"Result: {success}/{total} downloaded successfully")
    if args.dry_run:
        print("(dry run — nothing was actually downloaded)")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
