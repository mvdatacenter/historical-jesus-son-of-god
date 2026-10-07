#!/usr/bin/env python3
"""
Tests for translate_book.py
"""

import json

import pytest
from pathlib import Path
from translate_book import (
    split_into_fragments,
    split_at_paragraphs,
    normalize_language,
    create_translation_prompt,
    check_generated_translations,
    generated_translation_files,
    record_generated_translation,
    DEFAULT_FRAGMENT_SIZE,
    GENERATED_MANIFEST,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


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


GITATTRIBUTES = (
    "translations/*/preface_*.tex linguist-generated=true\n"
    "translations/*/chapter*_*.tex linguist-generated=true\n"
    "translations/*/epilogue_*.tex linguist-generated=true\n"
)
SOURCE = "\\section{One}\\label{sec:one}\nText \\cite{key:a} and \\ref{sec:two}.\n"
TRANSLATION = "\\section{Jeden}\\label{sec:one}\nTekst \\cite{key:a} i \\ref{sec:two}.\n"


def _repo(tmp_path):
    (tmp_path / ".gitattributes").write_text(GITATTRIBUTES, encoding="utf-8")
    (tmp_path / "chapter1.tex").write_text(SOURCE, encoding="utf-8")
    out = tmp_path / "translations" / "polish"
    out.mkdir(parents=True)
    (out / "manuscript_po.tex").write_text("hand authored master\n", encoding="utf-8")
    return tmp_path, out


def _written_by_the_script(tmp_path):
    root, out = _repo(tmp_path)
    target = out / "chapter1_po.tex"
    target.write_text(TRANSLATION, encoding="utf-8")
    record_generated_translation(target, root / "chapter1.tex")
    return root, out, target


class TestGeneratedTranslationsAreHeldToTheirManifest:
    def test_the_committed_generated_translations_match_their_manifest(self):
        assert check_generated_translations(REPO_ROOT) == []

    def test_the_gitattributes_patterns_select_the_generated_files_and_leave_the_master_out(self):
        rel = [p.relative_to(REPO_ROOT).as_posix() for p in generated_translation_files(REPO_ROOT)]
        assert "translations/polish/chapter4_po.tex" in rel
        assert "translations/polish/preface_po.tex" in rel
        assert "translations/polish/epilogue_po.tex" in rel
        assert "translations/polish/manuscript_po.tex" not in rel
        assert "translations/README.md" not in rel
        assert "translations/polish/" + GENERATED_MANIFEST not in rel

    def test_a_file_the_script_wrote_passes(self, tmp_path):
        root, out, target = _written_by_the_script(tmp_path)
        entry = json.loads((out / GENERATED_MANIFEST).read_text(encoding="utf-8"))["chapter1_po.tex"]
        assert entry["source"] == "chapter1.tex"
        assert entry["written_by"] == "scripts/translate_book.py"
        assert check_generated_translations(root) == []

    def test_a_line_changed_by_hand_after_the_script_wrote_the_file_fails(self, tmp_path):
        root, out, target = _written_by_the_script(tmp_path)
        target.write_text(TRANSLATION.replace("Tekst", "Inny tekst"), encoding="utf-8")
        problems = check_generated_translations(root)
        assert len(problems) == 1
        assert problems[0].startswith("translations/polish/chapter1_po.tex: sha256 ")
        assert "rerun the script instead of editing the file" in problems[0]

    def test_a_generated_file_with_no_manifest_entry_fails(self, tmp_path):
        root, out = _repo(tmp_path)
        (out / "chapter1_po.tex").write_text(TRANSLATION, encoding="utf-8")
        problems = check_generated_translations(root)
        assert problems == [
            "translations/polish/chapter1_po.tex: no entry in translations/polish/" + GENERATED_MANIFEST
            + "; a generated translation is written by scripts/translate_book.py, which records it"
        ]

    def test_a_manifest_entry_whose_file_is_gone_fails(self, tmp_path):
        root, out, target = _written_by_the_script(tmp_path)
        target.unlink()
        assert check_generated_translations(root) == [
            "translations/polish/chapter1_po.tex: recorded in " + GENERATED_MANIFEST + " but not present"
        ]

    def test_a_translation_missing_a_cite_of_its_unchanged_source_fails(self, tmp_path):
        root, out = _repo(tmp_path)
        target = out / "chapter1_po.tex"
        target.write_text(TRANSLATION.replace(" \\cite{key:a}", ""), encoding="utf-8")
        record_generated_translation(target, root / "chapter1.tex")
        assert check_generated_translations(root) == [
            "translations/polish/chapter1_po.tex: cites: missing ['key:a'] against chapter1.tex"
        ]

    def test_a_source_changed_after_the_translation_was_written_is_not_compared(self, tmp_path):
        root, out, target = _written_by_the_script(tmp_path)
        (root / "chapter1.tex").write_text(SOURCE + "New sentence \\cite{key:b}.\n", encoding="utf-8")
        assert check_generated_translations(root) == []

    def test_the_hand_authored_master_is_outside_the_check(self, tmp_path):
        root, out, target = _written_by_the_script(tmp_path)
        (out / "manuscript_po.tex").write_text("edited master\n", encoding="utf-8")
        assert check_generated_translations(root) == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
