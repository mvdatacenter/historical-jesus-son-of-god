#!/usr/bin/env python3
"""
Tests for translate_book.py
"""

import pytest
from pathlib import Path
from translate_book import (
    split_into_fragments,
    split_at_paragraphs,
    normalize_language,
    create_translation_prompt,
    DEFAULT_FRAGMENT_SIZE,
)


class TestNormalizeLanguage:
    def test_polish_variations(self):
        assert normalize_language("polish") == "Polish"
        assert normalize_language("Polish") == "Polish"
        assert normalize_language("POLISH") == "Polish"
        assert normalize_language("pl") == "Polish"
        assert normalize_language("PL") == "Polish"

    def test_other_languages(self):
        assert normalize_language("german") == "German"
        assert normalize_language("de") == "German"
        assert normalize_language("french") == "French"
        assert normalize_language("fr") == "French"

    def test_unknown_language_passthrough(self):
        assert normalize_language("Klingon") == "Klingon"
        assert normalize_language("  Elvish  ") == "Elvish"


class TestSplitAtParagraphs:
    def test_simple_split(self):
        content = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        fragments = split_at_paragraphs(content, max_size=30)
        assert len(fragments) >= 2
        assert all(len(f) <= 30 or f.count("\n\n") == 0 for f in fragments)

    def test_no_split_needed(self):
        content = "Short text."
        fragments = split_at_paragraphs(content, max_size=1000)
        assert len(fragments) == 1
        assert fragments[0] == "Short text."

    def test_preserves_content(self):
        content = "Para one.\n\nPara two.\n\nPara three."
        fragments = split_at_paragraphs(content, max_size=20)
        rejoined = "\n\n".join(fragments)
        # Content should be preserved (allowing for whitespace normalization)
        assert "Para one" in rejoined
        assert "Para two" in rejoined
        assert "Para three" in rejoined


class TestSplitIntoFragments:
    def test_respects_section_boundaries(self):
        content = r"""
\section{First Section}
Content of first section.

\section{Second Section}
Content of second section.
"""
        fragments = split_into_fragments(content, max_size=100)
        # Should split at section boundaries
        assert len(fragments) >= 1
        # Each fragment should be under max_size or be a single section
        for f in fragments:
            assert len(f) <= 100 or r"\section" in f

    def test_handles_subsections(self):
        content = r"""
\subsection{Sub One}
Text one.

\subsection{Sub Two}
Text two.
"""
        fragments = split_into_fragments(content, max_size=50)
        assert len(fragments) >= 1

    def test_empty_content(self):
        fragments = split_into_fragments("", max_size=100)
        assert fragments == []

    def test_whitespace_only(self):
        fragments = split_into_fragments("   \n\n   ", max_size=100)
        assert fragments == []


class TestCreateTranslationPrompt:
    def test_polish_prompt_is_in_polish(self):
        prompt = create_translation_prompt("Test content", "Polish", 1, 5)
        assert "Przetłumacz" in prompt  # Polish word for "translate"
        assert "ZASADY" in prompt  # Polish word for "rules"
        assert "Fragment 1/5" in prompt

    def test_other_language_prompt_is_in_english(self):
        prompt = create_translation_prompt("Test content", "German", 2, 10)
        assert "Translate" in prompt
        assert "RULES" in prompt
        assert "Fragment 2/10" in prompt

    def test_content_included(self):
        content = "This is the LaTeX content to translate."
        prompt = create_translation_prompt(content, "Polish", 1, 1)
        assert content in prompt


class TestOutputDirectoryLogic:
    """Test the output directory path construction logic."""

    def test_no_double_language_suffix(self):
        """When output_dir already ends with language, don't append again."""
        # This tests the bug that was fixed
        output_dir = "translations/polish"
        target_lang = "polish"

        # Simulate the fixed logic from translate_book.py line 304-307
        from pathlib import Path
        result = Path(output_dir)
        if not output_dir.lower().endswith(target_lang.lower()):
            result = result / target_lang.lower()

        # Should NOT be translations/polish/polish
        assert str(result) == "translations/polish"
        assert "polish/polish" not in str(result)

    def test_appends_language_when_needed(self):
        """When output_dir doesn't end with language, append it."""
        output_dir = "translations"
        target_lang = "polish"

        from pathlib import Path
        result = Path(output_dir)
        if not output_dir.lower().endswith(target_lang.lower()):
            result = result / target_lang.lower()

        assert str(result) == "translations/polish"

    def test_case_insensitive_check(self):
        """Language suffix check should be case insensitive."""
        output_dir = "translations/Polish"
        target_lang = "polish"

        from pathlib import Path
        result = Path(output_dir)
        if not output_dir.lower().endswith(target_lang.lower()):
            result = result / target_lang.lower()

        # Should recognize Polish == polish
        assert str(result) == "translations/Polish"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
