from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, HttpUrl, ConfigDict

class IngestUrlRequest(BaseModel):
    url: str

class IngestResponse(BaseModel):
    document_id: str
    job_id: str
    status: str
    message: str

class DocumentBase(BaseModel):
    title: str
    source_type: str
    source_url: Optional[str] = None
    original_filename: Optional[str] = None
    file_size_bytes: Optional[int] = None
    summary_short: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    chunk_count: Optional[int] = 0

class DocumentDetailResponse(DocumentResponse):
    raw_text_preview: Optional[str] = None
    has_analyses: bool = False
    analyses_count: int = 0
