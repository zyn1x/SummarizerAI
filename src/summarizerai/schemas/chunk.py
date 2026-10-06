from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class ChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None
    timestamp_formatted: Optional[str] = None
    token_count: Optional[int] = None
    metadata_json: Optional[Dict[str, Any]] = None
