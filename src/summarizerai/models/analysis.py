import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from summarizerai.database.base import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False) # summary, key_points, actionable_insights
    summary_format: Mapped[str | None] = mapped_column(String(50), nullable=True) # executive, detailed, bulleted
    user_goal: Mapped[str | None] = mapped_column(String(100), nullable=True) # e.g. study_exam, implement_method, apply_project, research_gaps, presentation
    
    result_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    key_takeaways_json: Mapped[list | None] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    document = relationship("Document", back_populates="analyses")
    citations = relationship("Citation", back_populates="analysis", cascade="all, delete-orphan")
