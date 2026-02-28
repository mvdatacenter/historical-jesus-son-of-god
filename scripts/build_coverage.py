#!/usr/bin/env python3
"""
build_coverage.py — DD-0002 Step 1 batch preparation and verdict management.

Manages the full-scale coverage evaluation pipeline:
1. Parses all Alexandria extraction findings
2. Groups findings by chapter
3. Excludes already-evaluated findings
4. Generates evaluation batches for agent processing
5. Merges agent verdicts into per-chapter verdict files

Usage:
    python scripts/build_coverage.py --status               # Pipeline status
    python scripts/build_coverage.py --batches               # Generate all batches
    python scripts/build_coverage.py --batches --chapter 3    # Ch3 batches only
    python scripts/build_coverage.py --merge FILE --chapter 3 # Merge verdicts
    python scripts/build_coverage.py --normalize              # Normalize formats
    python scripts/build_coverage.py --redistribute           # Redistribute wrong_chapter (round 1)
    python scripts/build_coverage.py --redistribute --round 2 # Round 2+ redistribution
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = PROJECT_ROOT / "sources"
YOUTUBE_DIR = SOURCES_DIR / "youtube"
COVERAGE_DIR = SOURCES_DIR / "coverage"

BATCH_SIZE = 15  # findings per evaluation batch

# Import the existing extraction parser
sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_extractions import parse_all_extractions


def load_inventory(chapter: int) -> list:
    """Load the coverage inventory for a chapter."""
    path = COVERAGE_DIR / f"ch{chapter}_inventory.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


def load_verdicts(chapter: int) -> dict:
    """Load existing verdicts for a chapter. Returns {finding_id: verdict_dict}."""
    path = COVERAGE_DIR / f"ch{chapter}_validation_verdicts.json"
    if not path.exists():
        return {}

    data = json.loads(path.read_text())

    # Normalize: dict format (ch3) → standard lookup
    if isinstance(data, dict):
        result = {}
        for fid, v in data.items():
            verdict = v.get("verdict") or v.get("step1_verdict", "")
            result[fid] = {
                "finding_id": fid,
                "verdict": verdict,
                "justification": v.get("justification", ""),
            }
        return result

    # Array format (all other chapters)
    result = {}
    for entry in data:
        fid = entry.get("finding_id", "")
        if fid:
            result[fid] = entry
    return result


def save_verdicts(chapter: int, verdicts: dict):
    """Save verdicts in standardized array format."""
    path = COVERAGE_DIR / f"ch{chapter}_validation_verdicts.json"
    # Convert to sorted array
    arr = sorted(verdicts.values(), key=lambda x: x.get("finding_id", ""))
    path.write_text(json.dumps(arr, indent=2, ensure_ascii=False))


def get_all_findings_by_chapter() -> dict:
    """Parse all extractions and group by primary chapter."""
    findings = parse_all_extractions()
    by_chapter = defaultdict(list)
    for f in findings:
        for ch in f.chapter_nums:
            by_chapter[ch].append(f)
    return by_chapter


def cmd_status(args):
    """Show pipeline status."""
    by_chapter = get_all_findings_by_chapter()

    print("DD-0002 Step 1 Pipeline Status")
    print("=" * 65)
    print(f"{'Ch':<4} {'Total':<8} {'Evaluated':<10} {'Remaining':<10} {'Inventory':<10}")
    print("-" * 65)

    total_all = 0
    eval_all = 0

    for ch in sorted(by_chapter.keys()):
        if ch == 0:
            continue  # skip preface
        total = len(by_chapter[ch])
        verdicts = load_verdicts(ch)
        evaluated = len(verdicts)
        inventory = load_inventory(ch)
        inv_count = len(inventory)
        remaining = total - evaluated

        total_all += total
        eval_all += evaluated

        print(f"Ch{ch:<3} {total:<8} {evaluated:<10} {remaining:<10} {inv_count:<10}")

    print("-" * 65)
    print(f"{'All':<4} {total_all:<8} {eval_all:<10} {total_all - eval_all:<10}")

    # Show verdict distribution for evaluated findings
    print("\nVerdict Distribution (evaluated findings):")
    all_verdicts = Counter()
    for ch in sorted(by_chapter.keys()):
        if ch == 0:
            continue
        verdicts = load_verdicts(ch)
        for v in verdicts.values():
            verdict = v.get("verdict", "unknown")
            all_verdicts[verdict] += 1

    for verdict, count in all_verdicts.most_common():
        pct = count / eval_all * 100 if eval_all > 0 else 0
        print(f"  {verdict:<16} {count:>4} ({pct:.1f}%)")


def cmd_batches(args):
    """Generate evaluation batches."""
    by_chapter = get_all_findings_by_chapter()
    chapters = [args.chapter] if args.chapter else sorted(ch for ch in by_chapter if ch > 0)

    COVERAGE_DIR.mkdir(parents=True, exist_ok=True)
    batches_dir = COVERAGE_DIR / "batches"
    batches_dir.mkdir(parents=True, exist_ok=True)

    total_batches = 0

    for ch in chapters:
        findings = by_chapter.get(ch, [])
        if not findings:
            print(f"Ch{ch}: No findings")
            continue

        # Load existing verdicts to exclude
        existing = load_verdicts(ch)
        unevaluated = [f for f in findings if f.finding_id not in existing]

        if not unevaluated:
            print(f"Ch{ch}: All {len(findings)} findings already evaluated")
            continue

        # Load inventory
        inventory = load_inventory(ch)
        if not inventory:
            print(f"Ch{ch}: WARNING — no inventory found, skipping")
            continue

        # Generate batches
        ch_batches = []
        for i in range(0, len(unevaluated), BATCH_SIZE):
            batch_findings = unevaluated[i:i + BATCH_SIZE]
            batch = {
                "chapter": ch,
                "batch_index": len(ch_batches),
                "total_batches_for_chapter": -1,  # filled below
                "findings": [
                    {
                        "finding_id": f.finding_id,
                        "channel": f.channel,
                        "video_title": f.video_title,
                        "status": f.status,
                        "description": f.description,
                        "quote": f.quote,
                    }
                    for f in batch_findings
                ],
            }
            ch_batches.append(batch)

        # Fill total count
        for b in ch_batches:
            b["total_batches_for_chapter"] = len(ch_batches)

        # Write batch files
        for b in ch_batches:
            batch_path = batches_dir / f"ch{ch}_batch_{b['batch_index']:03d}.json"
            batch_path.write_text(json.dumps(b, indent=2, ensure_ascii=False))

        total_batches += len(ch_batches)
        print(f"Ch{ch}: {len(unevaluated)} unevaluated findings → {len(ch_batches)} batches")

    print(f"\nTotal: {total_batches} batches written to {batches_dir}/")


def cmd_merge(args):
    """Merge agent verdict results into chapter verdict files."""
    if not args.chapter:
        print("ERROR: --chapter required with --merge", file=sys.stderr)
        return 1

    merge_path = Path(args.merge)
    if not merge_path.exists():
        print(f"ERROR: {merge_path} not found", file=sys.stderr)
        return 1

    new_data = json.loads(merge_path.read_text())

    # Support both array and dict formats from agents
    new_verdicts = {}
    if isinstance(new_data, list):
        for entry in new_data:
            fid = entry.get("finding_id", "")
            if fid:
                new_verdicts[fid] = entry
    elif isinstance(new_data, dict):
        for fid, v in new_data.items():
            new_verdicts[fid] = {"finding_id": fid, **v}

    existing = load_verdicts(args.chapter)
    added = 0
    updated = 0
    for fid, verdict in new_verdicts.items():
        if fid in existing:
            updated += 1
        else:
            added += 1
        existing[fid] = verdict

    save_verdicts(args.chapter, existing)
    print(f"Ch{args.chapter}: merged {added} new + {updated} updated → {len(existing)} total")


def cmd_normalize(args):
    """Normalize all verdict files to array format."""
    for ch in range(1, 7):
        verdicts = load_verdicts(ch)
        if not verdicts:
            continue
        save_verdicts(ch, verdicts)
        print(f"Ch{ch}: normalized {len(verdicts)} verdicts to array format")


MAX_REDISTRIB_ROUNDS = 3


def parse_target_chapter(entry: dict, source_ch: int) -> int | None:
    """Extract target chapter from a wrong_chapter verdict.

    Handles three formats:
    1. explicit suggested_chapter field (int like 4, or string like "ch5")
    2. regex "Chapter N" in justification text
    3. regex "Chapter N" in rationale text
    Returns target chapter int, or None if unparseable.
    """
    # Method 1: explicit suggested_chapter field
    sc = entry.get("suggested_chapter")
    if sc is not None:
        if isinstance(sc, int):
            if 1 <= sc <= 6 and sc != source_ch:
                return sc
        elif isinstance(sc, str):
            # Handle "ch5", "Ch3", "chapter 4", or bare "5"
            m = re.search(r"(\d)", sc)
            if m:
                ch = int(m.group(1))
                if 1 <= ch <= 6 and ch != source_ch:
                    return ch

    # Method 2/3: regex from justification or rationale
    text = entry.get("justification", "") or entry.get("rationale", "")
    if not text:
        return None

    matches = re.findall(r"[Cc]hapter\s*(\d)", text)
    targets = [int(m) for m in matches if int(m) != source_ch and 1 <= int(m) <= 6]
    if targets:
        return targets[0]

    # Also try "Ch3" / "ch5" patterns (common in verdict text)
    matches = re.findall(r"[Cc]h\s*(\d)", text)
    targets = [int(m) for m in matches if int(m) != source_ch and 1 <= int(m) <= 6]
    if targets:
        return targets[0]

    return None


def load_verdict_files(chapter: int, round_num: int) -> list[dict]:
    """Load verdict entries from appropriate files for a given round.

    Round 1: scans ch{N}_verdicts_opus_*.json (main evaluation)
    Round 2+: scans ch{N}_verdicts_opus_redistrib_r{round-1}.json only
    """
    entries = []

    if round_num == 1:
        # Main evaluation: all opus verdict files (excluding redistrib files)
        pattern = f"ch{chapter}_verdicts_opus_*.json"
        for path in sorted(COVERAGE_DIR.glob(pattern)):
            if "redistrib" in path.name:
                continue
            data = json.loads(path.read_text())
            if isinstance(data, list):
                entries.extend(data)
            elif isinstance(data, dict):
                for fid, v in data.items():
                    entries.append({"finding_id": fid, **v})

        # Also check consolidated validation_verdicts
        val_path = COVERAGE_DIR / f"ch{chapter}_validation_verdicts.json"
        if val_path.exists():
            data = json.loads(val_path.read_text())
            seen = {e.get("finding_id") for e in entries}
            if isinstance(data, list):
                for e in data:
                    if e.get("finding_id") not in seen:
                        entries.append(e)
            elif isinstance(data, dict):
                for fid, v in data.items():
                    if fid not in seen:
                        entries.append({"finding_id": fid, **v})
    else:
        # Round 2+: only previous round's redistribution verdicts
        prev = round_num - 1
        pattern = f"ch{chapter}_verdicts_opus_redistrib_r{prev}.json"
        path = COVERAGE_DIR / pattern
        if path.exists():
            data = json.loads(path.read_text())
            if isinstance(data, list):
                entries.extend(data)
            elif isinstance(data, dict):
                for fid, v in data.items():
                    entries.append({"finding_id": fid, **v})

    return entries


def cmd_redistribute(args):
    """Redistribute wrong_chapter findings to correct chapters."""
    round_num = args.round or 1

    if round_num > MAX_REDISTRIB_ROUNDS:
        print(f"ERROR: max {MAX_REDISTRIB_ROUNDS} redistribution rounds", file=sys.stderr)
        return 1

    # Build finding content lookup from parse_all_extractions()
    all_findings = parse_all_extractions()
    content_by_id = {}
    for f in all_findings:
        content_by_id[f.finding_id] = {
            "finding_id": f.finding_id,
            "text": f.description,
            "quote": f.quote,
        }

    # Fallback: alexandria_reextraction.json
    reextract_path = COVERAGE_DIR / "alexandria_reextraction.json"
    if reextract_path.exists():
        reextract = json.loads(reextract_path.read_text())
        for entry in reextract:
            fid = entry.get("finding_id", "")
            if fid and fid not in content_by_id:
                content_by_id[fid] = {
                    "finding_id": fid,
                    "text": entry.get("text", ""),
                    "quote": entry.get("quote", ""),
                }

    # Load previous-round redistribution history for ping-pong detection
    prev_redistributed = set()
    if round_num >= 2:
        for prev_round in range(1, round_num):
            for ch in range(1, 7):
                path = COVERAGE_DIR / f"ch{ch}_findings_redistrib_r{prev_round}.json"
                if path.exists():
                    data = json.loads(path.read_text())
                    for entry in data:
                        prev_redistributed.add(entry.get("finding_id", ""))

    # Collect wrong_chapter verdicts from all chapters
    # Key: target_chapter -> list of {finding_id, text, quote, source_ch}
    by_target = defaultdict(list)
    unparseable = []
    ping_pong = []
    total_wrong = 0

    for source_ch in range(1, 7):
        entries = load_verdict_files(source_ch, round_num)
        for entry in entries:
            if entry.get("verdict") != "wrong_chapter":
                continue

            total_wrong += 1
            fid = entry.get("finding_id", "")

            target = parse_target_chapter(entry, source_ch)
            if target is None:
                unparseable.append((fid, source_ch, entry))
                continue

            # Ping-pong detection: finding redistributed in a previous round
            if fid in prev_redistributed:
                ping_pong.append((fid, source_ch, target))
                continue

            # Look up content
            content = content_by_id.get(fid)
            if content is None:
                print(f"  WARNING: no content for {fid} (source ch{source_ch})")
                continue

            # Safety: target must differ from source
            if target == source_ch:
                continue

            by_target[target].append({
                "finding_id": fid,
                "text": content["text"],
                "quote": content["quote"],
                "source_chapter": source_ch,
            })

    # Print summary
    print(f"Redistribution Round {round_num}")
    print("=" * 55)
    print(f"Total wrong_chapter verdicts: {total_wrong}")

    if not by_target:
        print("\nNo findings to redistribute. Converged.")
        if unparseable:
            print(f"\n{len(unparseable)} unparseable (no target chapter detected):")
            for fid, sch, _ in unparseable:
                print(f"  {fid} (from ch{sch})")
        if ping_pong:
            print(f"\n{len(ping_pong)} ping-pong (flagged for manual review):")
            for fid, sch, tgt in ping_pong:
                print(f"  {fid}: ch{sch} → ch{tgt}")
        return 0

    print(f"\nRedistribution:")
    total_redistributed = 0
    for target_ch in sorted(by_target.keys()):
        findings = by_target[target_ch]
        sources = Counter(f["source_chapter"] for f in findings)
        source_str = ", ".join(f"ch{s}:{c}" for s, c in sorted(sources.items()))
        print(f"  → Ch{target_ch}: {len(findings)} findings (from {source_str})")
        total_redistributed += len(findings)

    # Write batch files
    COVERAGE_DIR.mkdir(parents=True, exist_ok=True)
    files_written = []

    for target_ch in sorted(by_target.keys()):
        findings = by_target[target_ch]
        out_path = COVERAGE_DIR / f"ch{target_ch}_findings_redistrib_r{round_num}.json"
        out_data = [
            {
                "finding_id": f["finding_id"],
                "text": f["text"],
                "quote": f["quote"],
                "source_chapter": f["source_chapter"],
            }
            for f in findings
        ]
        out_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False))
        files_written.append(out_path.name)

    print(f"\n{total_redistributed} findings → {len(files_written)} batch files:")
    for name in files_written:
        print(f"  {COVERAGE_DIR / name}")

    if unparseable:
        print(f"\n{len(unparseable)} unparseable (no target chapter detected):")
        for fid, sch, _ in unparseable:
            print(f"  {fid} (from ch{sch})")

    if ping_pong:
        print(f"\n{len(ping_pong)} ping-pong (flagged for manual review):")
        for fid, sch, tgt in ping_pong:
            print(f"  {fid}: ch{sch} → ch{tgt}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="DD-0002 Step 1 coverage pipeline management"
    )
    parser.add_argument("--status", action="store_true", help="Show pipeline status")
    parser.add_argument("--batches", action="store_true", help="Generate eval batches")
    parser.add_argument("--merge", type=str, help="Merge verdict results from file")
    parser.add_argument("--normalize", action="store_true", help="Normalize formats")
    parser.add_argument("--redistribute", action="store_true",
                        help="Redistribute wrong_chapter findings")
    parser.add_argument("--round", type=int, default=1,
                        help="Redistribution round number (default: 1)")
    parser.add_argument("--chapter", type=int, help="Limit to specific chapter")
    args = parser.parse_args()

    if args.status:
        return cmd_status(args)
    elif args.batches:
        return cmd_batches(args)
    elif args.merge:
        return cmd_merge(args)
    elif args.normalize:
        return cmd_normalize(args)
    elif args.redistribute:
        return cmd_redistribute(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
