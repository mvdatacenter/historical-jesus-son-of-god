#!/usr/bin/env python3
"""
build_coverage.py — DD-0002 pipeline: Step 1 verdicts + Step 2 embed context.

Step 1 (verdict management):
    python scripts/build_coverage.py --status               # Pipeline status
    python scripts/build_coverage.py --batches               # Generate all batches
    python scripts/build_coverage.py --batches --chapter 3    # Ch3 batches only
    python scripts/build_coverage.py --merge FILE --chapter 3 # Merge verdicts
    python scripts/build_coverage.py --normalize              # Normalize formats
    python scripts/build_coverage.py --redistribute           # Redistribute wrong_chapter
    python scripts/build_coverage.py --redistribute --round 2 # Round 2+

Step 2 (embed context assembly):
    python scripts/build_coverage.py --embed-prep --chapter 4 # Step 2 context packages
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

BATCH_SIZE = 250  # findings per batch — see DD-0002 for calculation

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
    """Generate self-contained evaluation batches.

    Each batch includes: findings, chapter inventory, full chapter text,
    cross-chapter inventories, and anti-pattern rules. The evaluating
    agent does not need to load anything separately.
    """
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

        if args.force:
            unevaluated = findings
        else:
            existing = load_verdicts(ch)
            unevaluated = [f for f in findings if f.finding_id not in existing]

        if not unevaluated:
            print(f"Ch{ch}: All {len(findings)} findings already evaluated")
            continue

        inventory = load_inventory(ch)
        if not inventory:
            print(f"Ch{ch}: WARNING — no inventory found, skipping")
            continue

        # Context: chapter text + Q&A + cross-chapter inventories (shared across batches)
        chapter_path = PROJECT_ROOT / f"chapter{ch}.tex"
        chapter_text = chapter_path.read_text() if chapter_path.exists() else ""

        qa_path = PROJECT_ROOT / "scripts" / f"ch{ch}_qa.md"
        qa_text = qa_path.read_text() if qa_path.exists() else ""

        cross_chapter = {}
        for other_ch in range(1, 7):
            if other_ch == ch:
                continue
            inv = load_inventory(other_ch)
            if inv:
                cross_chapter[f"chapter_{other_ch}"] = inv

        # Generate batches
        ch_batches = []
        for i in range(0, len(unevaluated), BATCH_SIZE):
            batch_findings = unevaluated[i:i + BATCH_SIZE]
            batch = {
                "chapter": ch,
                "batch_index": len(ch_batches),
                "total_batches_for_chapter": -1,  # filled below
                "anti_pattern_rules": ANTI_PATTERN_RULES,
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
                "chapter_inventory": inventory,
                "chapter_text": chapter_text,
                "qa_history": qa_text,
                "cross_chapter_inventories": cross_chapter,
            }
            ch_batches.append(batch)

        for b in ch_batches:
            b["total_batches_for_chapter"] = len(ch_batches)

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


STEP2_RULES = [
    (
        "Step 2 verdicts — every verdict must include a justification: "
        "EMBED: finding is core to an argument, substantive (a concrete text, "
        "inscription, historical fact — not just a scholar restating the thesis), "
        "and grounded enough to write now. "
        "RESEARCH: finding is potentially high value but needs sourcing before "
        "it can be written. Goes to research_gaps.md with what source is needed "
        "and where to look. Nothing is rejected for being 'unverified' or "
        "'speculative.' ChatGPT's inability to find a source means nothing. "
        "SKIP: tangential — true but the book doesn't need it. "
        "SKIP: restates — scholar says what the book already argues in different "
        "words. Adding it makes the argument longer, not stronger. "
        "SKIP: weak — too thin to strengthen anything."
    ),
    (
        "CRITICAL: No finding may be rejected because ChatGPT cannot verify it. "
        "'ChatGPT says it's unsubstantiated' is not a SKIP reason — it is a "
        "RESEARCH reason. ChatGPT lies often due to bias. It halluccinates "
        "sources, fabricates references, and presents its gaps as fact. Listen "
        "to ChatGPT, never trust it. 'ChatGPT confirmed X' is a lead, not "
        "verification. 'ChatGPT couldn't find X' means nothing."
    ),
    (
        "Cross-chapter check: if another chapter contains a deeper or more "
        "developed treatment of the same argument, the new material belongs "
        "there — merged into the existing section, not duplicated. The goal "
        "is one authoritative treatment per argument, not parallel versions."
    ),
    (
        "Section-fit check: before inserting text into a specific section, "
        "verify (1) the new text does not contradict the chapter's own thesis, "
        "and (2) the new text serves the argument of the section it is placed "
        "in. If the text doesn't serve the section's argument, find the section "
        "it does serve — or create one."
    ),
    (
        "Q&A check: if the Q&A file records a deliberate decision to exclude "
        "something, respect it. Do not resurface findings that were already "
        "researched and rejected."
    ),
]


ANTI_PATTERN_RULES = [
    (
        "Keyword extraction is forbidden in any form: extracting words from "
        "text A, searching for them in text B, and drawing any conclusion "
        "from matches. See PM-0001, PM-0002."
    ),
    (
        "Scripts present information for human review. Scripts never assign "
        "verdicts based on mechanical text matching."
    ),
    (
        "No automated status assignment (CLEAR, FLAGGED, NEEDS_REVIEW, KEEP, "
        "SKIP) based on text matching."
    ),
    (
        "COVERED verdict anti-patterns — three forbidden shortcuts: "
        "(1) Topic-level match: 'book argues X, finding argues X, therefore "
        "covered' is WRONG. Must name the specific evidence the finding brings "
        "AND where the book already presents that same specific evidence. "
        "(2) 'Same argument' without evidence comparison: 'ch1 makes this exact "
        "argument' is not enough. Does the book already present this specific "
        "scholar's framing, this specific quote, this specific example? If any "
        "of these are new, verdict is new_evidence, not covered. "
        "(3) Implicit coverage: 'the concept is implicit in the framework' or "
        "'this is a variant of what is covered' means the book does NOT state it "
        "— therefore NOT covered. Any of these make it new_evidence: a named "
        "concept the book doesn't use, a specific mechanism the book doesn't "
        "describe, a new scope claim, or a new specific source text (e.g., book "
        "has Mark-Homer mimesis but finding has Mark-Aeneid — different source, "
        "not a variant). Test: does the inventory list this exact item? If you "
        "must argue it is 'implied by' or 'a variant of' an existing item, it "
        "is NOT covered."
    ),
]


def _load_v2_verdicts(ch: int) -> dict:
    """Load v2 verdicts (list format from Step 1 re-run). Returns {finding_id: entry}."""
    path = COVERAGE_DIR / f"ch{ch}_verdicts_v2.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    result = {}
    if isinstance(data, list):
        for entry in data:
            fid = entry.get("finding_id", "")
            if fid:
                result[fid] = entry
    return result


STEP1_SURVIVORS = ("new_argument", "new_evidence", "contradicts")


def _load_findings_from_verdicts(ch: int) -> list[dict]:
    """Load surviving findings from Step 1 verdicts.

    Checks v2 verdicts first (current pipeline), falls back to
    validation_verdicts (legacy). Survivors: new_argument, new_evidence,
    contradicts.
    """
    verdicts = _load_v2_verdicts(ch)
    if not verdicts:
        verdicts = load_verdicts(ch)
        verdicts = {fid: v for fid, v in verdicts.items()}

    survivors = [
        v for v in verdicts.values()
        if v.get("verdict") in STEP1_SURVIVORS
    ]

    # Enrich with content from extraction files
    all_findings = parse_all_extractions()
    content_by_id = {f.finding_id: f for f in all_findings}

    for fallback_name in ("all_new_arguments.json", "alexandria_reextraction.json"):
        fallback_path = COVERAGE_DIR / fallback_name
        if not fallback_path.exists():
            continue
        for entry in json.loads(fallback_path.read_text()):
            fid = entry.get("finding_id", "")
            if not fid or fid in content_by_id:
                continue
            content_by_id[fid] = type("Finding", (), {
                "finding_id": fid,
                "description": entry.get("text", ""),
                "quote": entry.get("quote", ""),
                "video_title": entry.get("video_title", ""),
                "channel": entry.get("channel", ""),
            })()

    packages = []
    for v in sorted(survivors, key=lambda x: x.get("finding_id", "")):
        fid = v.get("finding_id", "")
        content = content_by_id.get(fid)
        packages.append({
            "finding_id": fid,
            "step1_verdict": v.get("verdict", ""),
            "step1_justification": v.get("justification", ""),
            "text": content.description if content else "",
            "quote": getattr(content, "quote", ""),
            "source": (
                getattr(content, "video_title", "")
                or getattr(content, "channel", "")
            ),
        })
    return packages


def _load_findings_from_batch(batch_path: Path) -> dict[int, list[dict]]:
    """Load findings from a batch file, grouped by chapter."""
    data = json.loads(batch_path.read_text())
    by_chapter = defaultdict(list)
    for entry in data:
        ch = entry.get("chapter")
        if not ch:
            continue
        by_chapter[ch].append({
            "finding_id": entry.get("finding_id", ""),
            "step1_verdict": "batch",
            "step1_justification": entry.get("justification", ""),
            "text": entry.get("text", ""),
            "quote": entry.get("quote", ""),
            "source": entry.get("source", ""),
        })
    return dict(by_chapter)


def _build_chapter_context(ch: int, findings: list[dict]) -> dict:
    """Build a Step 2 context package for one chapter.

    Includes everything the evaluator needs: findings, chapter text,
    chapter inventory, Q&A, cross-chapter inventories, anti-pattern
    rules, and Step 2 verdict rules. The evaluator does not need to
    load anything separately.
    """
    qa_path = PROJECT_ROOT / "scripts" / f"ch{ch}_qa.md"
    qa_text = qa_path.read_text() if qa_path.exists() else ""

    chapter_path = PROJECT_ROOT / f"chapter{ch}.tex"
    chapter_text = chapter_path.read_text() if chapter_path.exists() else ""

    chapter_inventory = load_inventory(ch)

    cross_chapter = {}
    for other_ch in range(1, 7):
        if other_ch == ch:
            continue
        inv = load_inventory(other_ch)
        if inv:
            cross_chapter[f"chapter_{other_ch}"] = inv

    return {
        "chapter": ch,
        "step2_rules": STEP2_RULES,
        "anti_pattern_rules": ANTI_PATTERN_RULES,
        "findings": findings,
        "qa_history": qa_text,
        "chapter_text": chapter_text,
        "chapter_inventory": chapter_inventory,
        "cross_chapter_inventories": cross_chapter,
    }


def cmd_embed_prep(args):
    """Assemble Step 2 embed context packages.

    Two modes:
      --embed-prep --chapter N           Survivors from Step 1 verdicts
      --embed-prep --batch FILE          Findings from a batch file

    Each context package contains: findings, anti-pattern rules, Q&A
    history, full chapter text, and cross-chapter inventories.

    The tool assembles and presents. It does not score, classify, or
    pre-filter. See DD-0002 Step 2 spec.
    """
    out_dir = COVERAGE_DIR / "embed_prep"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print(f"ERROR: {batch_path} not found", file=sys.stderr)
            return 1
        by_chapter = _load_findings_from_batch(batch_path)
        chapters = sorted(by_chapter.keys())
    elif args.chapter:
        findings = _load_findings_from_verdicts(args.chapter)
        if not findings:
            print(f"Ch{args.chapter}: No surviving findings for embedding")
            return 0
        by_chapter = {args.chapter: findings}
        chapters = [args.chapter]
    else:
        # All chapters
        by_chapter = {}
        for ch in range(1, 7):
            findings = _load_findings_from_verdicts(ch)
            if findings:
                by_chapter[ch] = findings
        chapters = sorted(by_chapter.keys())
        if not chapters:
            print("No surviving findings in any chapter")
            return 0

    for ch in chapters:
        findings = by_chapter[ch]
        output = _build_chapter_context(ch, findings)
        out_path = out_dir / f"ch{ch}_embed_context.json"
        out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))

        print(f"Ch{ch}: {len(findings)} findings → {out_path}")
        for p in findings:
            print(f"  {p['finding_id']:30s}  {p['step1_verdict']:15s}  "
                  f"{p['text'][:60]}...")

    total = sum(len(by_chapter[ch]) for ch in chapters)
    print(f"\nTotal: {total} findings across {len(chapters)} chapters")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="DD-0002 coverage pipeline (Step 1 verdicts + Step 2 embed context)"
    )
    parser.add_argument("--status", action="store_true", help="Show pipeline status")
    parser.add_argument("--batches", action="store_true", help="Generate eval batches")
    parser.add_argument("--merge", type=str, help="Merge verdict results from file")
    parser.add_argument("--normalize", action="store_true", help="Normalize formats")
    parser.add_argument("--redistribute", action="store_true",
                        help="Redistribute wrong_chapter findings")
    parser.add_argument("--embed-prep", action="store_true",
                        help="Assemble Step 2 embed context packages")
    parser.add_argument("--batch", type=str,
                        help="Batch file for --embed-prep (findings JSON)")
    parser.add_argument("--round", type=int, default=1,
                        help="Redistribution round number (default: 1)")
    parser.add_argument("--chapter", type=int, help="Limit to specific chapter")
    parser.add_argument("--force", action="store_true",
                        help="Regenerate batches for ALL findings (ignore existing verdicts)")
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
    elif args.embed_prep:
        return cmd_embed_prep(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
