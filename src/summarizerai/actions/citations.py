import re
from typing import List, Dict, Any, Tuple
from summarizerai.models.chunk import Chunk

def extract_deterministic_citations(
    text_content: str,
    chunks: List[Chunk]
) -> List[Dict[str, Any]]:
    """
    Generate deterministic backend-controlled citations.
    Scans the synthesized content against the ground-truth chunks to anchor
    evidence to real page numbers, timestamps, and section headings.
    Ensures the LLM cannot hallucinate citations.
    """
    citations: List[Dict[str, Any]] = []
    seen_labels = set()

    # Pre-index chunks by keywords and sentences
    chunk_data = []
    for c in chunks:
        # Determine label and type
        if c.page_number is not None:
            label = f"[p. {c.page_number}]"
            c_type = "page"
        elif c.timestamp_formatted:
            label = f"[{c.timestamp_formatted}]"
            c_type = "timestamp"
        elif c.section_heading:
            clean_head = c.section_heading.strip()
            if len(clean_head) > 24:
                clean_head = clean_head[:21] + "..."
            label = f"[{clean_head}]"
            c_type = "section"
        else:
            label = f"[Chunk {c.chunk_index + 1}]"
            c_type = "chunk"

        # Extract words for match scoring
        words = set(re.findall(r"\b\w{4,}\b", c.content.lower()))
        chunk_data.append({
            "chunk": c,
            "label": label,
            "type": c_type,
            "words": words,
            "content": c.content
        })

    # Break text into paragraphs / key claims
    paragraphs = [p.strip() for p in text_content.split("\n\n") if p.strip()]

    for p in paragraphs:
        if p.startswith("#") or len(p) < 40:
            continue
        p_words = set(re.findall(r"\b\w{4,}\b", p.lower()))
        if not p_words:
            continue

        best_score = 0.0
        best_match = None

        for item in chunk_data:
            # pyrefly: ignore [unsupported-operation]
            intersection = len(p_words & item["words"])
            if intersection > 0:
                score = intersection / (len(p_words) + 1e-5)
                if score > best_score and score >= 0.15:
                    best_score = score
                    best_match = item

        if best_match:
            chunk = best_match["chunk"]
            label = best_match["label"]
            if label not in seen_labels:
                seen_labels.add(label)
                
                # Extract a concise representative quote from the chunk
                # pyrefly: ignore [missing-attribute]
                sentences = re.split(r"(?<=[.!?])\s+", chunk.content)
                # pyrefly: ignore [missing-attribute]
                quote = sentences[0] if sentences else chunk.content[:150]
                if len(quote) > 180:
                    quote = quote[:177] + "..."

                citations.append({
                    # pyrefly: ignore [missing-attribute]
                    "chunk_id": chunk.id,
                    "citation_label": label,
                    "citation_type": best_match["type"],
                    # pyrefly: ignore [missing-attribute]
                    "page_number": chunk.page_number,
                    # pyrefly: ignore [missing-attribute]
                    "section_heading": chunk.section_heading,
                    # pyrefly: ignore [missing-attribute]
                    "timestamp_formatted": chunk.timestamp_formatted,
                    # pyrefly: ignore [missing-attribute]
                    "timestamp_seconds": chunk.timestamp_start,
                    "quote_text": quote.strip(),
                })

    # If no citations were matched above (e.g. short document), include the primary chunk citations
    if not citations and chunks:
        for c in chunks[:3]:
            if c.page_number is not None:
                lbl = f"[p. {c.page_number}]"
                ctype = "page"
            elif c.timestamp_formatted:
                lbl = f"[{c.timestamp_formatted}]"
                ctype = "timestamp"
            elif c.section_heading:
                lbl = f"[{c.section_heading[:20]}]"
                ctype = "section"
            else:
                lbl = f"[Chunk {c.chunk_index + 1}]"
                ctype = "chunk"

            sentences = re.split(r"(?<=[.!?])\s+", c.content)
            quote = sentences[0] if sentences else c.content[:150]

            citations.append({
                "chunk_id": c.id,
                "citation_label": lbl,
                "citation_type": ctype,
                "page_number": c.page_number,
                "section_heading": c.section_heading,
                "timestamp_formatted": c.timestamp_formatted,
                "timestamp_seconds": c.timestamp_start,
                "quote_text": quote.strip(),
            })

    return citations
