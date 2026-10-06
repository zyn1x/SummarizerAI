from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ActionType(str, Enum):
    SUMMARY = "summary"
    KEY_POINTS = "key_points"
    ACTIONABLE_INSIGHTS = "actionable_insights"

class SummaryFormat(str, Enum):
    EXECUTIVE = "executive"
    DETAILED = "detailed"
    BULLETED = "bulleted"

class UserGoal(str, Enum):
    STUDY_EXAM = "study_exam"
    UNDERSTAND_TOPIC = "understand_topic"
    IMPLEMENT_METHOD = "implement_method"
    APPLY_PROJECT = "apply_project"
    RESEARCH_GAPS = "find_research_gaps"
    PREPARE_PRESENTATION = "prepare_presentation"

class AnalysisRequest(BaseModel):
    action_type: ActionType
    summary_format: Optional[SummaryFormat] = SummaryFormat.EXECUTIVE
    force_refresh: bool = False

class ActionableInsightsRequest(BaseModel):
    user_goal: UserGoal
    custom_context: Optional[str] = None
    force_refresh: bool = False

class CitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    citation_label: str
    citation_type: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    timestamp_formatted: Optional[str] = None
    timestamp_seconds: Optional[float] = None
    quote_text: str
    chunk_id: str

class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    action_type: str
    summary_format: Optional[str] = None
    user_goal: Optional[str] = None
    result_markdown: str
    key_takeaways: Optional[List[str]] = []
    citations: Optional[List[CitationResponse]] = []
    created_at: datetime
    is_cached: bool = False
