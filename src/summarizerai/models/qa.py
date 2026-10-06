import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from summarizerai.database.base import Base

class QAInteraction(Base):
    __tablename__ = "qa_interactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_grounded: Mapped[bool] = mapped_column(default=True)
    citations_json: Mapped[list | None] = mapped_column(JSON, default=list) # [{label, type, target, quote, chunk_id}]
    retrieved_chunk_ids: Mapped[list | None] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationship
    document = relationship("Document", back_populates="qa_interactions")
