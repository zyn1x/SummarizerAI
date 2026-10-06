from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class JobStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    status: str  # uploading, extracting, normalizing, chunking, analyzing, ready, failed
    progress_percent: int
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
