from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CitationItem(BaseModel):
    chunk_id: str
    citation_label: str
    citation_type: str # page, section, timestamp
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    timestamp_formatted: Optional[str] = None
    timestamp_seconds: Optional[float] = None
    quote_text: str

class QARequest(BaseModel):
    question: str
    top_k: int = 5

class QAResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    question: str
    answer: str
    is_grounded: bool
    citations: List[CitationItem] = []
    created_at: datetime

class QAHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question: str
    answer: str
    is_grounded: bool
    citations_json: Optional[List[Dict[str, Any]]] = []
    created_at: datetime
