from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class CanonicalChunk:
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None
    timestamp_formatted: Optional[str] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    token_count: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_citation_label(self) -> str:
        """Generate deterministic citation label based on source type."""
        if self.page_number is not None:
            return f"[p. {self.page_number}]"
        elif self.timestamp_formatted:
            return f"[{self.timestamp_formatted}]"
        elif self.section_heading:
            clean_head = self.section_heading.strip()
            if len(clean_head) > 25:
                clean_head = clean_head[:22] + "..."
            return f"[{clean_head}]"
        return f"[Chunk {self.chunk_index + 1}]"

@dataclass
class CanonicalDocument:
    title: str
    source_type: str  # "pdf", "txt", "website", "youtube", "research_paper"
    source_url: Optional[str] = None
    original_filename: Optional[str] = None
    raw_text: str = ""
    file_size_bytes: Optional[int] = None
    chunks: List[CanonicalChunk] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
