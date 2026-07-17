#!/usr/bin/env python3
"""Regression tests for source registry metadata."""

from source_registry import SOURCES


def test_van_kooten_ekklesia_uses_correct_cambridge_doi():
    source = SOURCES["vankooten:ekklesia"]

    assert source["doi"] == "10.1017/S002868851200015X"
    assert source["obtain"] == "Cambridge Core."
    assert "S0028688512000148" not in repr(source)
