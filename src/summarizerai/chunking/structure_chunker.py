import re
from typing import List, Optional
from summarizerai.processing.canonical import CanonicalChunk

def estimate_tokens(text: str) -> int:
    """Rough approximation of tokens: ~1 token per 4 characters or ~0.75 words."""
    return max(1, len(text.split()))

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences cleanly."""
    # Split on sentence terminals while keeping punctuation
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]

def chunk_text_with_metadata(
    text: str,
    target_words: int = 250,
    overlap_words: int = 40,
    page_number: Optional[int] = None,
    section_heading: Optional[str] = None,
    timestamp_start: Optional[float] = None,
    timestamp_end: Optional[float] = None,
    timestamp_formatted: Optional[str] = None,
    start_chunk_idx: int = 0
) -> List[CanonicalChunk]:
    """
    Split text into structure-aware chunks respecting sentence boundaries
    and preserving source metadata.
    """
    sentences = split_into_sentences(text)
    if not sentences:
        if text.strip():
            return [
                CanonicalChunk(
                    chunk_index=start_chunk_idx,
                    content=text.strip(),
                    page_number=page_number,
                    section_heading=section_heading,
                    timestamp_start=timestamp_start,
                    timestamp_end=timestamp_end,
                    timestamp_formatted=timestamp_formatted,
                    token_count=estimate_tokens(text)
                )
            ]
        return []

    chunks: List[CanonicalChunk] = []
    current_sentences: List[str] = []
    current_word_count = 0
    chunk_idx = start_chunk_idx

    for sentence in sentences:
        words_in_sent = len(sentence.split())
        if current_word_count + words_in_sent > target_words and current_sentences:
            chunk_content = " ".join(current_sentences)
            chunks.append(
                CanonicalChunk(
                    chunk_index=chunk_idx,
                    content=chunk_content,
                    page_number=page_number,
                    section_heading=section_heading,
                    timestamp_start=timestamp_start,
                    timestamp_end=timestamp_end,
                    timestamp_formatted=timestamp_formatted,
                    token_count=estimate_tokens(chunk_content)
                )
            )
            chunk_idx += 1

            # Keep overlap sentences from the end
            overlap_sentences: List[str] = []
            overlap_count = 0
            for s in reversed(current_sentences):
                w = len(s.split())
                if overlap_count + w <= overlap_words:
                    overlap_sentences.insert(0, s)
                    overlap_count += w
                else:
                    break
            
            current_sentences = overlap_sentences + [sentence]
            current_word_count = overlap_count + words_in_sent
        else:
            current_sentences.append(sentence)
            current_word_count += words_in_sent

    # Add remaining sentences
    if current_sentences:
        chunk_content = " ".join(current_sentences)
        chunks.append(
            CanonicalChunk(
                chunk_index=chunk_idx,
                content=chunk_content,
                page_number=page_number,
                section_heading=section_heading,
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                timestamp_formatted=timestamp_formatted,
                token_count=estimate_tokens(chunk_content)
            )
        )

    return chunks
