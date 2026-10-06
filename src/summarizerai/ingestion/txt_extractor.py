import os
from typing import List
from summarizerai.processing.canonical import CanonicalDocument, CanonicalChunk
from summarizerai.processing.normalizer import normalize_text, detect_sections
from summarizerai.chunking.structure_chunker import chunk_text_with_metadata

class TXTExtractionError(Exception):
    pass

def extract_txt_content(file_path: str, original_filename: str) -> CanonicalDocument:
    """
    Extract text from plain text or markdown files with multi-encoding fallback
    and section structure extraction.
    """
    if not os.path.exists(file_path):
        raise TXTExtractionError(f"File not found: {file_path}")

    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
    content = None
    used_encoding = None

    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
                used_encoding = enc
                break
        except UnicodeDecodeError:
            continue

    if content is None:
        raise TXTExtractionError("Unable to decode text file. Unsupported character encoding.")

    cleaned = normalize_text(content)
    if not cleaned.strip():
        raise TXTExtractionError("Text file is empty.")

    title = os.path.splitext(original_filename)[0].replace("_", " ").title()

    sections = detect_sections(cleaned)
    all_chunks: List[CanonicalChunk] = []
    chunk_index = 0

    for sec_heading, sec_text in sections:
        sec_chunks = chunk_text_with_metadata(
            text=sec_text,
            target_words=250,
            overlap_words=35,
            section_heading=sec_heading,
            start_chunk_idx=chunk_index
        )
        all_chunks.extend(sec_chunks)
        chunk_index += len(sec_chunks)

    return CanonicalDocument(
        title=title,
        source_type="txt",
        original_filename=original_filename,
        raw_text=cleaned,
        file_size_bytes=os.path.getsize(file_path),
        chunks=all_chunks,
        metadata={
            "encoding": used_encoding,
            "section_count": len(sections),
            "line_count": len(cleaned.splitlines()),
        }
    )
