#!/usr/bin/env python3
"""Regression tests for source registry metadata."""

import re
from pathlib import Path

from source_registry import SOURCES

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEX_FILES = sorted(PROJECT_ROOT.glob("preface.tex")) + \
    sorted(PROJECT_ROOT.glob("chapter*.tex")) + \
    sorted(PROJECT_ROOT.glob("epilogue.tex"))
CITE_KEY_PATTERN = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}")
BIB_KEY_PATTERN = re.compile(r"^@\w+\{([^,]+),", re.MULTILINE)


def cited_keys():
    keys = set()
    for tex_path in TEX_FILES:
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


def test_van_kooten_ekklesia_uses_correct_cambridge_doi():
    source = SOURCES["vankooten:ekklesia"]

    assert source["doi"] == "10.1017/S002868851200015X"
    assert source["obtain"] == "Cambridge Core."
    assert "S0028688512000148" not in repr(source)
