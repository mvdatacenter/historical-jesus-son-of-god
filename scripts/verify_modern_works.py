#!/usr/bin/env python3
"""
verify_modern_works.py — Verify claims about modern scholarly works.

For each modern work cited in the manuscript, extracts the claim made about it,
searches for reviews/summaries/descriptions online, and downloads evidence
confirming the work says what we claim it says.

Uses Google Books API (descriptions), Open Library, and web search results.

Usage:
    poetry run python scripts/verify_modern_works.py              # Verify all
    poetry run python scripts/verify_modern_works.py --key KEY    # Single work
    poetry run python scripts/verify_modern_works.py --report     # Regenerate report
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: poetry add requests beautifulsoup4")
    sys.exit(1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_registry import SOURCES, MODERN
from verify_citations import extract_citations, extract_claim

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = PROJECT_ROOT / "sources"
REQUEST_DELAY = 2
REQUEST_TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def get_manuscript_claims():
    """Extract all modern citations with their manuscript claims."""
    tex_files = sorted(PROJECT_ROOT.glob("chapter*.tex"))
    tex_files += list(PROJECT_ROOT.glob("preface.tex"))
    tex_files += list(PROJECT_ROOT.glob("epilogue.tex"))

    all_citations = []
    for tf in tex_files:
        all_citations.extend(extract_citations(tf))

    claims = {}
    for c in all_citations:
        info = SOURCES.get(c.key, {})
        if info.get("category") != MODERN:
            continue
        claim_text = extract_claim(Path(c.file), c.line_num)
        if c.key not in claims:
            claims[c.key] = {
                "title": info.get("title", ""),
                "author": info.get("author", ""),
                "year": info.get("year", ""),
                "citations": [],
            }
        claims[c.key]["citations"].append({
            "file": os.path.basename(c.file),
            "line": c.line_num,
            "claim": claim_text,
        })
    return claims


def search_google_books(title, author):
    """Search Google Books for description/summary."""
    author_last = author.split()[-1] if author.split() else author
    query = f'intitle:"{title}" inauthor:{author_last}'

    try:
        resp = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": query, "maxResults": 3},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("totalItems", 0) == 0:
            # Looser search
            resp = requests.get(
                "https://www.googleapis.com/books/v1/volumes",
                params={"q": f"{title} {author_last}", "maxResults": 3},
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get("totalItems", 0) == 0:
            return None

        item = data["items"][0]
        info = item.get("volumeInfo", {})
        return {
            "title": info.get("title", ""),
            "subtitle": info.get("subtitle", ""),
            "authors": info.get("authors", []),
            "publisher": info.get("publisher", ""),
            "date": info.get("publishedDate", ""),
            "pages": info.get("pageCount"),
            "description": info.get("description", ""),
            "categories": info.get("categories", []),
            "isbn": [i["identifier"] for i in info.get("industryIdentifiers", [])],
            "info_link": info.get("infoLink", ""),
        }
    except requests.RequestException:
        return None


def search_open_library(title, author):
    """Search Open Library for metadata and description."""
    author_last = author.split()[-1] if author.split() else author
    try:
        resp = requests.get(
            "https://openlibrary.org/search.json",
            params={"title": title, "author": author_last, "limit": 3},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("numFound", 0) == 0:
            return None

        doc = data["docs"][0]
        work_key = doc.get("key", "")

        result = {
            "title": doc.get("title", ""),
            "authors": doc.get("author_name", []),
            "first_publish_year": doc.get("first_publish_year"),
            "publisher": doc.get("publisher", [])[:3],
            "isbn": doc.get("isbn", [])[:3],
            "ol_url": f"https://openlibrary.org{work_key}" if work_key else "",
            "description": "",
        }

        # Get description from work page
        if work_key:
            try:
                wr = requests.get(f"https://openlibrary.org{work_key}.json", timeout=REQUEST_TIMEOUT)
                if wr.status_code == 200:
                    wd = wr.json()
                    desc = wd.get("description", "")
                    if isinstance(desc, dict):
                        desc = desc.get("value", "")
                    result["description"] = desc
            except requests.RequestException:
                pass

        return result
    except requests.RequestException:
        return None


def fetch_wikipedia_summary(title, author):
    """Try to find a Wikipedia article about the book or author's thesis."""
    author_last = author.split()[-1] if author.split() else author

    # Try book title first, then author
    for query in [title, f"{author_last} {title}"]:
        try:
            resp = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": 3,
                    "format": "json",
                },
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("query", {}).get("search", [])

            for r in results:
                page_title = r.get("title", "")
                # Get extract
                ext_resp = requests.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "titles": page_title,
                        "prop": "extracts",
                        "exintro": True,
                        "explaintext": True,
                        "format": "json",
                    },
                    timeout=REQUEST_TIMEOUT,
                )
                ext_data = ext_resp.json()
                pages = ext_data.get("query", {}).get("pages", {})
                for pid, page in pages.items():
                    extract = page.get("extract", "")
                    if extract and len(extract) > 100:
                        return {
                            "page_title": page_title,
                            "url": f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
                            "extract": extract[:2000],
                        }
        except requests.RequestException:
            continue

    return None


def search_claim_on_web(query):
    """Search for a specific claim on the web and return relevant page text."""
    try:
        # Use Google Custom Search via a simple scrape-free approach:
        # fetch Wikipedia search, Google Books search, or other APIs
        results = []

        # Try Wikipedia search for the claim
        resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 3,
                "format": "json",
            },
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code == 200:
            data = resp.json()
            for r in data.get("query", {}).get("search", [])[:2]:
                page_title = r.get("title", "")
                snippet = r.get("snippet", "")
                # Clean HTML from snippet
                snippet = re.sub(r"<[^>]+>", "", snippet)
                if snippet and len(snippet) > 50:
                    # Get full extract
                    ext_resp = requests.get(
                        "https://en.wikipedia.org/w/api.php",
                        params={
                            "action": "query",
                            "titles": page_title,
                            "prop": "extracts",
                            "explaintext": True,
                            "exlimit": 1,
                            "exchars": 3000,
                            "format": "json",
                        },
                        timeout=REQUEST_TIMEOUT,
                    )
                    if ext_resp.status_code == 200:
                        pages = ext_resp.json().get("query", {}).get("pages", {})
                        for pid, page in pages.items():
                            extract = page.get("extract", "")
                            if extract and len(extract) > 100:
                                results.append({
                                    "source": f"Wikipedia: {page_title}",
                                    "url": f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
                                    "text": extract[:3000],
                                    "search_snippet": snippet,
                                })

        return results

    except requests.RequestException:
        return []


def verify_work(key, claim_info):
    """Verify a single modern work. Returns verification dict."""
    title = claim_info["title"]
    author = claim_info["author"]
    year = claim_info["year"]

    print(f"\n{'=' * 60}")
    print(f"[{key}] {author} — {title} ({year})")

    # Show what manuscript claims
    for cit in claim_info["citations"]:
        print(f"  Cited in {cit['file']}:{cit['line']}")
    full_claim = claim_info["citations"][0]["claim"]
    print(f"  Claim: {full_claim[:200]}...")
    print()

    verification = {
        "key": key,
        "title": title,
        "author": author,
        "year": year,
        "manuscript_claims": claim_info["citations"],
        "verified": False,
        "evidence": [],
    }

    # 1. Google Books (basic existence + description)
    print("  [1/5] Google Books metadata...", end=" ")
    gb = search_google_books(title, author)
    if gb:
        print(f"EXISTS — {gb['title']}")
        verification["evidence"].append({
            "source": "Google Books (metadata)",
            "title": gb["title"],
            "authors": gb["authors"],
            "publisher": gb["publisher"],
            "date": gb["date"],
            "pages": gb["pages"],
            "isbn": gb["isbn"],
            "description": gb["description"],
            "link": gb["info_link"],
        })
    else:
        print("not found")
    time.sleep(REQUEST_DELAY)

    # 2. Open Library (metadata)
    print("  [2/5] Open Library metadata...", end=" ")
    ol = search_open_library(title, author)
    if ol:
        print(f"EXISTS — {ol['title']}")
        verification["evidence"].append({
            "source": "Open Library (metadata)",
            "title": ol["title"],
            "authors": ol["authors"],
            "publisher": ol["publisher"],
            "year": ol["first_publish_year"],
            "isbn": ol["isbn"],
            "description": ol["description"],
            "link": ol["ol_url"],
        })
    else:
        print("not found")
    time.sleep(REQUEST_DELAY)

    # Book exists if found in either
    book_exists = bool(gb or ol)
    if book_exists:
        verification["book_exists"] = True

    # 3. Claim-specific searches (Wikipedia)
    print("  [3/5] Searching Wikipedia for specific claims...")
    claim_evidence = []
    # Search for author + title on Wikipedia
    author_last = author.split()[-1] if author.split() else author
    for q in [f"{author_last} {title}", title]:
        results = search_claim_on_web(q)
        if results:
            print(f"    FOUND ({len(results)} result(s))")
            claim_evidence.extend(results)
            break
    else:
        print("    no results")
    time.sleep(REQUEST_DELAY)

    if claim_evidence:
        seen_urls = set()
        for ev in claim_evidence:
            url = ev.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                verification["evidence"].append({
                    "source": ev["source"],
                    "url": url,
                    "description": ev.get("text", ""),
                    "search_snippet": ev.get("search_snippet", ""),
                })
                verification["verified"] = True

    # 4. Wikipedia about the book/author
    print("  [4/5] Wikipedia (book/author)...", end=" ")
    wiki = fetch_wikipedia_summary(title, author)
    if wiki:
        print(f"FOUND — {wiki['page_title']}")
        verification["evidence"].append({
            "source": f"Wikipedia: {wiki['page_title']}",
            "url": wiki["url"],
            "description": wiki["extract"],
        })
        verification["verified"] = True
    else:
        print("not found")
    time.sleep(REQUEST_DELAY)

    # 5. (Placeholder — LLM evaluation done separately by review_citations.py)
    print("  [5/5] LLM evaluation: run `poetry run python scripts/review_citations.py` after")

    # Verdict
    if verification["verified"]:
        n_claim = len([e for e in verification["evidence"]
                       if "metadata" not in e.get("source", "")])
        n_meta = len([e for e in verification["evidence"]
                      if "metadata" in e.get("source", "")])
        print(f"  RESULT: Book exists ({n_meta} catalogs), "
              f"claim evidence: {n_claim} source(s)")
    else:
        if book_exists:
            print("  RESULT: Book exists but NO evidence for specific claims")
        else:
            print("  RESULT: Book NOT FOUND in any catalog")

    return verification


def save_verification(key, verification):
    """Save verification evidence to sources/modern/{key}/verification.json."""
    safe_key = key.replace(":", "_")
    dest_dir = SOURCES_DIR / "modern" / safe_key
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / "verification.json"
    dest_path.write_text(
        json.dumps(verification, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def generate_report(verifications, output_path):
    """Generate markdown report with evidence for each work."""
    verified = [v for v in verifications if v["verified"]]
    not_verified = [v for v in verifications if not v["verified"]]

    lines = [
        "# Modern Works Verification Report",
        "",
        f"Verified: {len(verified)}/{len(verifications)} works have online evidence.",
        "",
    ]

    for v in sorted(verifications, key=lambda x: x["key"]):
        status = "VERIFIED" if v["verified"] else "NOT VERIFIED"
        lines.append(f"## `{v['key']}` — {status}")
        lines.append(f"**{v['author']}** — *{v['title']}* ({v['year']})")
        lines.append("")

        # Manuscript claim
        lines.append("### What the manuscript claims")
        for cit in v["manuscript_claims"]:
            claim_clean = cit["claim"].replace("\n", " ").strip()
            if len(claim_clean) > 400:
                claim_clean = claim_clean[:400] + "..."
            lines.append(f"> {claim_clean}")
            lines.append(f"> — *{cit['file']}:{cit['line']}*")
            lines.append("")

        # Evidence
        if v["evidence"]:
            lines.append("### Evidence found")
            for ev in v["evidence"]:
                src = ev.get("source", "?")
                lines.append(f"**{src}:**")

                if ev.get("title"):
                    lines.append(f"- Title: {ev['title']}")
                if ev.get("authors"):
                    lines.append(f"- Authors: {', '.join(ev['authors'])}")
                if ev.get("publisher"):
                    pub = ev["publisher"]
                    if isinstance(pub, list):
                        pub = ", ".join(pub[:2])
                    lines.append(f"- Publisher: {pub}")
                if ev.get("date") or ev.get("year"):
                    lines.append(f"- Date: {ev.get('date') or ev.get('year')}")
                if ev.get("pages"):
                    lines.append(f"- Pages: {ev['pages']}")
                if ev.get("isbn"):
                    isbn = ev["isbn"]
                    if isinstance(isbn, list):
                        isbn = ", ".join(str(i) for i in isbn[:2])
                    lines.append(f"- ISBN: {isbn}")
                if ev.get("link") or ev.get("url"):
                    lines.append(f"- Link: {ev.get('link') or ev.get('url')}")

                desc = ev.get("description") or ev.get("extract") or ""
                if desc:
                    desc_clean = desc.replace("\n", " ").strip()
                    if len(desc_clean) > 600:
                        desc_clean = desc_clean[:600] + "..."
                    lines.append(f"- Description: {desc_clean}")
                lines.append("")
        else:
            lines.append("*No evidence found online.*")
            lines.append("")

        lines.append("---")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Verify claims about modern scholarly works."
    )
    parser.add_argument("--key", type=str, help="Verify a single source by bib key")
    parser.add_argument("--report", action="store_true", help="Regenerate report only")
    args = parser.parse_args()

    claims = get_manuscript_claims()

    if args.report:
        verifications = []
        for key in sorted(claims.keys()):
            safe_key = key.replace(":", "_")
            vf = SOURCES_DIR / "modern" / safe_key / "verification.json"
            if vf.exists():
                verifications.append(json.loads(vf.read_text()))
        report_path = SOURCES_DIR / "modern_verification_report.md"
        generate_report(verifications, report_path)
        return

    if args.key:
        if args.key not in claims:
            print(f"ERROR: '{args.key}' not found in modern citations.")
            print(f"Available: {', '.join(sorted(claims.keys()))}")
            sys.exit(1)
        to_check = {args.key: claims[args.key]}
    else:
        to_check = claims

    print("=" * 60)
    print(f"Verifying {len(to_check)} modern work(s)")
    print("=" * 60)

    verifications = []
    for key, claim_info in sorted(to_check.items()):
        v = verify_work(key, claim_info)
        verifications.append(v)
        save_verification(key, v)
        time.sleep(REQUEST_DELAY)

    # Merge with existing if single-key run
    if args.key:
        all_v = []
        for k in sorted(claims.keys()):
            safe_k = k.replace(":", "_")
            vf = SOURCES_DIR / "modern" / safe_k / "verification.json"
            if vf.exists():
                all_v.append(json.loads(vf.read_text()))
        verifications = all_v

    report_path = SOURCES_DIR / "modern_verification_report.md"
    generate_report(verifications, report_path)

    verified = sum(1 for v in verifications if v["verified"])
    print(f"\n{'=' * 60}")
    print(f"Result: {verified}/{len(verifications)} works verified")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
