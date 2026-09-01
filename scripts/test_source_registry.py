#!/usr/bin/env python3
"""Regression tests for source registry metadata."""

import re
from pathlib import Path

import subprocess

from source_registry import SOURCES
from translate_book import get_all_chapters

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEX_FILES = sorted(PROJECT_ROOT.glob("preface.tex")) + \
    sorted(PROJECT_ROOT.glob("chapter*.tex")) + \
    sorted(PROJECT_ROOT.glob("epilogue.tex"))
TRANSLATION_TEX_FILES = sorted(PROJECT_ROOT.glob("translations/*/*.tex"))
TRANSLATION_MASTERS = sorted(PROJECT_ROOT.glob("translations/*/manuscript_*.tex"))
ALL_TEX_FILES = TEX_FILES + TRANSLATION_TEX_FILES
CITE_KEY_PATTERN = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}")
BIB_KEY_PATTERN = re.compile(r"^@\w+\{([^,]+),", re.MULTILINE)


def cited_keys():
    keys = set()
    for tex_path in ALL_TEX_FILES:
        for line in tex_path.read_text(encoding="utf-8").split("\n"):
            if line.lstrip().startswith("%"):
                continue
            for match in CITE_KEY_PATTERN.finditer(line):
                keys.update(k.strip() for k in match.group(1).split(","))
    return keys


def test_every_cited_key_has_a_bibliography_entry():
    bib_text = (PROJECT_ROOT / "references.bib").read_text(encoding="utf-8")
    bib_keys = set(BIB_KEY_PATTERN.findall(bib_text))

    missing = sorted(cited_keys() - bib_keys)
    assert missing == [], f"Cited keys missing from references.bib: {missing}"


def test_every_cited_key_has_a_registry_entry():
    missing = sorted(cited_keys() - set(SOURCES))
    assert missing == [], f"Cited keys missing from source_registry.py: {missing}"


BOOK_CITE_PATTERN = re.compile(r"\\cite\[(\d+)\.[^\]]*\]\{([^}]+)\}")


def book_numbered_cites():
    cites = set()
    for tex_path in ALL_TEX_FILES:
        for line in tex_path.read_text(encoding="utf-8").split("\n"):
            if line.lstrip().startswith("%"):
                continue
            for match in BOOK_CITE_PATTERN.finditer(line):
                for key in match.group(2).split(","):
                    cites.add((key.strip(), int(match.group(1))))
    return cites


def test_every_book_numbered_cite_has_a_covering_book_url():
    """A cite like [37.18] into a source whose URLs are book-keyed needs a URL
    covering that book (book37, or a split key like book2a or book16ch2).
    Without one the locator falls back to the other books' files and can
    present a same-numbered section from the wrong book as LOCATED."""
    uncovered = []
    for key, book in sorted(book_numbered_cites()):
        source = SOURCES.get(key)
        if not source:
            continue
        url_keys = [k for k in source.get("urls", {}) if re.match(r"book\d", k)]
        if not url_keys:
            continue
        if any(re.match(rf"book{book}(\D|$)", k) for k in url_keys):
            continue
        uncovered.append((key, book))
    assert uncovered == [], (
        f"Book-numbered cites without a covering registry URL: {uncovered}"
    )


def test_van_kooten_ekklesia_uses_correct_cambridge_doi():
    source = SOURCES["vankooten:ekklesia"]

    assert source["doi"] == "10.1017/S002868851200015X"
    assert source["obtain"] == "Cambridge Core."
    assert "S0028688512000148" not in repr(source)


ADDBIBRESOURCE_PATTERN = re.compile(r"\\addbibresource\{([^}]+)\}")


def test_every_translated_edition_loads_the_bibliography():
    """A translation with no bibliography cannot carry a citation at all. The
    Polish master loaded no biblatex and printed no reference list, so its
    readers got the claims without the sources and any ported cite would have
    failed to resolve (#175)."""
    assert TRANSLATION_MASTERS, "No translated edition found under translations/"

    problems = []
    for master in TRANSLATION_MASTERS:
        name = master.relative_to(PROJECT_ROOT).as_posix()
        text = master.read_text(encoding="utf-8")
        resources = ADDBIBRESOURCE_PATTERN.findall(text)
        if not resources:
            problems.append(f"{name}: no \\addbibresource")
        for resource in resources:
            if not (master.parent / resource).exists():
                problems.append(f"{name}: \\addbibresource{{{resource}}} does not resolve")
        if "\\printbibliography" not in text:
            problems.append(f"{name}: no \\printbibliography")
    assert problems == [], (
        "Translated editions without a bibliography:\n" + "\n".join(problems)
    )


CITE_COMMAND_PATTERN = re.compile(r"\\(?:no)?cite[a-zA-Z]*(?:\[[^\]]*\])*\{[^}]*\}")

OPTIONAL_POLISH_CASE_ENDING = r"(?:owie|ami|ach|iem|ego|emu|owi|owa|ów|ie|em|im|ym|y|i|e|u|a)?"

MOUNTAIN_BEFORE_TABOR = re.compile(r"(?:Mount|Mt\.|G[oó]r(?:a|y|ę|ą|ze|e))\s+$")

def modern_scholar_surnames():
    """Surnames of the modern scholars the bibliography carries, read from the
    keywords={modern} entries of references.bib. Ancient authors and eponymous
    standards fall outside that partition, as they fall outside the rule."""
    bib_text = (PROJECT_ROOT / "references.bib").read_text(encoding="utf-8")
    surnames = set()
    for entry in re.split(r"(?m)^@", bib_text)[1:]:
        if not re.search(r"keywords\s*=\s*\{[^}]*modern[^}]*\}", entry, re.I):
            continue
        field = re.search(r"(?m)^\s*(?:author|editor)\s*=\s*\{(.+?)\},?\s*$", entry)
        if not field or field.group(1).startswith("{"):
            continue  # corporate author, e.g. {The Royal Household}
        for person in field.group(1).split(" and "):
            person = person.strip()
            family = person.split(",")[0] if "," in person else person.rsplit(" ", 1)[-1]
            token = family.split()[-1].split("-")[-1]
            if len(token) >= 4 and token[0].isupper():
                surnames.add(token)
    return surnames


def scholars_named_in_prose():
    patterns = {
        surname: re.compile(r"(?<![\w\\])" + surname + OPTIONAL_POLISH_CASE_ENDING + r"(?![\w])")
        for surname in modern_scholar_surnames()
    }
    named = []
    for tex_path in ALL_TEX_FILES:
        name = tex_path.relative_to(PROJECT_ROOT).as_posix()
        for number, line in enumerate(tex_path.read_text(encoding="utf-8").split("\n"), 1):
            if line.lstrip().startswith("%"):
                continue
            prose = CITE_COMMAND_PATTERN.sub(" ", line)
            for surname, pattern in patterns.items():
                for match in pattern.finditer(prose):
                    if MOUNTAIN_BEFORE_TABOR.search(prose[:match.start()]):
                        continue
                    named.append(f"{name}:{number}: {surname}")
    return sorted(named)


def test_no_modern_scholar_is_named_in_prose():
    """docs/REVIEW.md holds a modern scholar's name to the inside of a cite, so
    the reader is handed the work rather than the reputation. Both editions are in
    scope, and Polish inflects: "Harnack" is written "Harnacka" after "od", so a
    word boundary straight after the nominative form is the wrong end of the
    match, and one case ending is allowed for."""
    named = scholars_named_in_prose()
    assert named == [], (
        "Modern scholars named outside a citation:\n" + "\n".join(named)
    )


GIT_VALUES_MEANING_NOT_GENERATED = {"unspecified", "unset", "false"}


def declared_generated(paths):
    """What .gitattributes says linguist-generated is for each path, read
    through git so the pattern semantics are git's own."""
    result = subprocess.run(
        ["git", "check-attr", "linguist-generated", "--", *paths],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    declared = {}
    for line in result.stdout.splitlines():
        path, _, value = line.rsplit(": ", 2)
        declared[path] = value
    return declared


def test_generated_marks_exactly_what_the_translation_pipeline_writes():
    """translate_book.py writes one <stem>_<language>.tex per English source it
    translates, and the translated master is not among them. Marking the whole
    of translations/ generated therefore marked the one file that can give a
    translated edition its bibliography as output a rerun would replace, when no
    rerun writes it at all (#175)."""
    pipeline_stems = [Path(path).stem for path in get_all_chapters(str(PROJECT_ROOT))]
    assert pipeline_stems, "translate_book.py reports no source chapters"

    wrong = []
    directories = sorted(
        path for path in (PROJECT_ROOT / "translations").iterdir() if path.is_dir()
    )
    for directory in directories:
        paths = [
            tex.relative_to(PROJECT_ROOT).as_posix()
            for tex in sorted(directory.glob("*.tex"))
        ]
        declared = declared_generated(paths)
        for path in paths:
            stem = Path(path).stem
            written = any(stem.startswith(f"{source}_") for source in pipeline_stems)
            if written and declared[path] in GIT_VALUES_MEANING_NOT_GENERATED:
                wrong.append(f"{path}: translate_book.py writes it, not marked generated")
            if not written and declared[path] not in GIT_VALUES_MEANING_NOT_GENERATED:
                wrong.append(f"{path}: marked generated, but no pipeline run writes it")
    assert wrong == [], "Generated marking does not match the pipeline:\n" + "\n".join(wrong)
