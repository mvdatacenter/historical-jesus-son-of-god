"""
Shared text utilities for translation and TTS scripts.
"""

import re
from typing import List


def split_into_fragments(content: str, max_size: int = 15000) -> List[str]:
    """Split LaTeX content into fragments at natural boundaries.

    Tries to split at:
    1. Section boundaries (\\section, \\subsection, etc.)
    2. Paragraph boundaries (blank lines)
    3. Sentence boundaries (. followed by space/newline)

    Never splits in the middle of:
    - LaTeX commands
    - Greek/Hebrew text blocks
    """
    fragments = []

    # First, try to split at major section boundaries
    section_pattern = r'(\\(?:sub)*section\{[^}]+\})'
    parts = re.split(section_pattern, content)

    current_fragment = ""

    for part in parts:
        # If adding this part would exceed max_size, save current and start new
        if len(current_fragment) + len(part) > max_size and current_fragment:
            # Try to find a good split point within current_fragment
            if len(current_fragment) > max_size:
                # Split at paragraph boundaries
                sub_fragments = split_at_paragraphs(current_fragment, max_size)
                fragments.extend(sub_fragments[:-1])
                current_fragment = sub_fragments[-1] if sub_fragments else ""
            else:
                fragments.append(current_fragment.strip())
                current_fragment = ""

        current_fragment += part

    # Don't forget the last fragment
    if current_fragment.strip():
        if len(current_fragment) > max_size:
            sub_fragments = split_at_paragraphs(current_fragment, max_size)
            fragments.extend(sub_fragments)
        else:
            fragments.append(current_fragment.strip())

    return [f for f in fragments if f.strip()]


def split_at_paragraphs(content: str, max_size: int) -> List[str]:
    """Split content at paragraph boundaries (blank lines)."""
    paragraphs = re.split(r'\n\s*\n', content)

    fragments = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 > max_size and current:
            fragments.append(current.strip())
            current = para
        else:
            if current:
                current += "\n\n" + para
            else:
                current = para

    if current.strip():
        fragments.append(current.strip())

    return fragments


def split_into_tts_chunks(text: str, max_chars: int = 4000) -> List[str]:
    """Split text into chunks suitable for TTS API (max 4096 chars).

    Uses the same logic as translation splitting but with smaller chunk size,
    and splits long paragraphs at sentence boundaries.
    """
    # First split at paragraph level using the same logic
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If paragraph itself is too long, split by sentences
        if len(para) > max_chars:
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 > max_chars:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk = current_chunk + " " + sentence if current_chunk else sentence
        elif len(current_chunk) + len(para) + 2 > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def strip_latex(text: str) -> str:
    """Remove LaTeX commands, keeping readable text for TTS."""
    # Remove comments
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)

    # Remove common structural commands entirely
    text = re.sub(r'\\(label|ref|cite|index|footnote|href)\{[^}]*\}', '', text)
    text = re.sub(r'\\(begin|end)\{[^}]*\}', '', text)
    text = re.sub(r'\\(section|subsection|paragraph|chapter)\*?\{([^}]*)\}', r'\2.', text)

    # Remove formatting commands, keeping content
    text = re.sub(r'\\(emph|textbf|textit|textsc)\{([^}]*)\}', r'\2', text)

    # Remove remaining backslash commands
    text = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?', '', text)

    # Clean up special chars
    text = text.replace('``', '"').replace("''", '"')
    text = text.replace('---', '—').replace('--', '–')
    text = text.replace('~', ' ')

    # Remove extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    return text.strip()
