import uuid
from sqlalchemy import String, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from summarizerai.database.base import Base

class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata and source locations
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True) # For PDFs
    section_heading: Mapped[str | None] = mapped_column(String(500), nullable=True) # For web / research papers
    timestamp_start: Mapped[float | None] = mapped_column(Float, nullable=True) # For YouTube (seconds)
    timestamp_end: Mapped[float | None] = mapped_column(Float, nullable=True) # For YouTube (seconds)
    timestamp_formatted: Mapped[str | None] = mapped_column(String(50), nullable=True) # e.g. "04:15"
    
    char_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    char_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Vector embedding serialized as JSON array of floats for cross-db compatibility (pgvector ready)
    embedding_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Relationship
    document = relationship("Document", back_populates="chunks")
    citations = relationship("Citation", back_populates="chunk", cascade="all, delete-orphan")
