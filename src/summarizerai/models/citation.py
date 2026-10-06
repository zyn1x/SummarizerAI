import uuid
from sqlalchemy import String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from summarizerai.database.base import Base

class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id: Mapped[str] = mapped_column(String(36), ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=True, index=True)
    
    citation_label: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "[p. 4]", "[Sec: Results]", "[02:45]"
    citation_type: Mapped[str] = mapped_column(String(50), default="page")    # page, section, timestamp
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_heading: Mapped[str | None] = mapped_column(String(500), nullable=True)
    timestamp_formatted: Mapped[str | None] = mapped_column(String(50), nullable=True)
    timestamp_seconds: Mapped[float | None] = mapped_column(nullable=True)
    quote_text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Relationships
    document = relationship("Document", back_populates="citations")
    chunk = relationship("Chunk", back_populates="citations")
    analysis = relationship("Analysis", back_populates="citations")
