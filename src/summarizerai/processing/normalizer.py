import re
import unicodedata
from typing import List, Tuple

def normalize_text(text: str) -> str:
    """Normalize unicode, whitespace, and fix hyphenated linebreaks."""
    if not text:
        return ""
    # NFKC normalization
    text = unicodedata.normalize("NFKC", text)
    # Fix hyphenated words broken across lines: e.g. "connec-\ntion" -> "connection"
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    # Replace multiple empty lines with maximum 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing/leading spaces on lines
    lines = [line.strip() for line in text.split("\n")]
    # Replace excessive horizontal whitespace with a single space
    lines = [re.sub(r"[ \t]+", " ", line) for line in lines]
    cleaned = "\n".join(lines).strip()
    return cleaned

def detect_sections(text: str) -> List[Tuple[str, str]]:
    """
    Split text into (heading, content) tuples.
    Recognizes markdown headings (# Heading), numbered sections (1. Introduction),
    and all-caps headings.
    """
    lines = text.split("\n")
    sections: List[Tuple[str, str]] = []
    current_heading = "Introduction"
    current_buffer: List[str] = []

    heading_patterns = [
        re.compile(r"^(#{1,4})\s+(.+)$"),                   # Markdown # Title
        re.compile(r"^(\d+\.?\d*)\s+([A-Z][A-Za-z0-9\s]{2,50})$"), # 1. Abstract / 2.1 Methods
        re.compile(r"^([A-Z\s]{3,40}):?$"),                # ALL CAPS SECTION
    ]

    for line in lines:
        trimmed = line.strip()
        matched = False
        for pattern in heading_patterns:
            m = pattern.match(trimmed)
            if m:
                # If we have buffered text, save previous section
                section_text = "\n".join(current_buffer).strip()
                if section_text:
                    sections.append((current_heading, section_text))
                current_buffer = []
                # Clean heading title
                if pattern.groups == 2:
                    current_heading = m.group(2).strip()
                else:
                    current_heading = trimmed.lstrip("# ").strip()
                matched = True
                break
        
        if not matched:
            current_buffer.append(line)

    # Append the last section
    section_text = "\n".join(current_buffer).strip()
    if section_text:
        sections.append((current_heading, section_text))

    if not sections and text.strip():
        sections.append(("Content", text.strip()))

    return sections
