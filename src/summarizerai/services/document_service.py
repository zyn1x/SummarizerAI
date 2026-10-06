import hashlib
import logging
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from summarizerai.models.document import Document
from summarizerai.models.chunk import Chunk
from summarizerai.models.job import ProcessingJob
from summarizerai.models.analysis import Analysis
from summarizerai.models.citation import Citation
from summarizerai.processing.canonical import CanonicalDocument
from summarizerai.llm.factory import get_llm_provider
from summarizerai.actions.summarizer import generate_hierarchical_summary
from summarizerai.actions.key_points import generate_key_points
from summarizerai.actions.actionable_insights import generate_actionable_insights

logger = logging.getLogger(__name__)

async def create_document_from_canonical(
    canonical_doc: CanonicalDocument,
    db: AsyncSession,
    job_id: Optional[str] = None
) -> Tuple[Document, ProcessingJob]:
    """
    Persist CanonicalDocument into database, create chunks with metadata and embeddings,
    and update the processing job.
    """
    # Compute content hash
    content_hash = hashlib.sha256(canonical_doc.raw_text.encode("utf-8")).hexdigest()

    # Check for existing document with same hash
    existing = await db.execute(select(Document).where(Document.content_hash == content_hash))
    matched_doc = existing.scalar_one_or_none()

    if matched_doc:
        # Re-use existing document
        if job_id:
            job_res = await db.execute(select(ProcessingJob).where(ProcessingJob.id == job_id))
            job = job_res.scalar_one_or_none()
            if job:
                job.status = "ready"
                job.progress_percent = 100
                job.current_step = "Document already ingested. Loaded from library."
                await db.commit()
        # pyrefly: ignore [bad-return]
        return matched_doc, None

    # Create new document
    doc = Document(
        title=canonical_doc.title,
        source_type=canonical_doc.source_type,
        source_url=canonical_doc.source_url,
        original_filename=canonical_doc.original_filename,
        file_size_bytes=canonical_doc.file_size_bytes,
        content_hash=content_hash,
        raw_text=canonical_doc.raw_text,
        metadata_json=canonical_doc.metadata,
    )
    db.add(doc)
    await db.flush()

    # Get job if provided
    job = None
    if job_id:
        job_res = await db.execute(select(ProcessingJob).where(ProcessingJob.id == job_id))
        job = job_res.scalar_one_or_none()
        if job:
            job.document_id = doc.id
            job.status = "chunking"
            job.progress_percent = 60
            job.current_step = f"Chunking content into structure-aware segments..."
            await db.commit()

    # Create chunks
    llm = await get_llm_provider()
    chunk_texts = [c.content for c in canonical_doc.chunks]
    
    # Pre-compute embeddings for vector search readiness
    embeddings = []
    try:
        embeddings = await llm.embed(chunk_texts)
    except Exception as e:
        logger.warning(f"Embedding generation deferred: {e}")

    for idx, c in enumerate(canonical_doc.chunks):
        emb = embeddings[idx] if idx < len(embeddings) else None
        db_chunk = Chunk(
            document_id=doc.id,
            chunk_index=c.chunk_index,
            content=c.content,
            page_number=c.page_number,
            section_heading=c.section_heading,
            timestamp_start=c.timestamp_start,
            timestamp_end=c.timestamp_end,
            timestamp_formatted=c.timestamp_formatted,
            token_count=c.token_count,
            embedding_json=emb,
            metadata_json=c.metadata,
        )
        db.add(db_chunk)

    if job:
        job.status = "analyzing"
        job.progress_percent = 85
        job.current_step = "Generating initial summary..."
        await db.commit()

    # Generate initial executive summary and cache it
    await db.flush()
    chunks_res = await db.execute(select(Chunk).where(Chunk.document_id == doc.id).order_by(Chunk.chunk_index))
    loaded_chunks = list(chunks_res.scalars().all())

    summary_text, citations_data = await generate_hierarchical_summary(loaded_chunks, llm, "executive")
    doc.summary_short = summary_text[:300] + "..." if len(summary_text) > 300 else summary_text

    initial_analysis = Analysis(
        document_id=doc.id,
        action_type="summary",
        summary_format="executive",
        result_markdown=summary_text,
    )
    db.add(initial_analysis)
    await db.flush()

    # Save citations
    for cit in citations_data:
        db_cit = Citation(
            document_id=doc.id,
            chunk_id=cit["chunk_id"],
            analysis_id=initial_analysis.id,
            citation_label=cit["citation_label"],
            citation_type=cit["citation_type"],
            page_number=cit.get("page_number"),
            section_heading=cit.get("section_heading"),
            timestamp_formatted=cit.get("timestamp_formatted"),
            timestamp_seconds=cit.get("timestamp_seconds"),
            quote_text=cit["quote_text"],
        )
        db.add(db_cit)

    if job:
        job.status = "ready"
        job.progress_percent = 100
        job.current_step = "Document ingested and ready for analysis."

    await db.commit()
    await db.refresh(doc)
    # pyrefly: ignore [bad-return]
    return doc, job

async def get_or_create_analysis(
    document_id: str,
    action_type: str,
    summary_format: Optional[str],
    user_goal: Optional[str],
    db: AsyncSession,
    force_refresh: bool = False
) -> Tuple[Analysis, bool]:
    """
    Check if analysis already exists in the database to reuse it,
    or generate and persist a new one.
    """
    if not force_refresh:
        query = select(Analysis).where(
            Analysis.document_id == document_id,
            Analysis.action_type == action_type,
        )
        if summary_format:
            query = query.where(Analysis.summary_format == summary_format)
        if user_goal:
            query = query.where(Analysis.user_goal == user_goal)

        res = await db.execute(query)
        existing = res.scalar_one_or_none()
        if existing:
            return existing, True

    # Need to generate fresh analysis
    chunks_res = await db.execute(
        select(Chunk).where(Chunk.document_id == document_id).order_by(Chunk.chunk_index)
    )
    chunks = list(chunks_res.scalars().all())
    if not chunks:
        raise ValueError("Document has no text chunks to analyze.")

    llm = await get_llm_provider()
    key_takeaways = []
    citations_data = []

    if action_type == "summary":
        result_markdown, citations_data = await generate_hierarchical_summary(
            chunks, llm, summary_format or "executive"
        )
    elif action_type == "key_points":
        result_markdown, key_takeaways, citations_data = await generate_key_points(chunks, llm)
    elif action_type == "actionable_insights":
        result_markdown, citations_data = await generate_actionable_insights(
            chunks, llm, user_goal or "understand_topic"
        )
    else:
        raise ValueError(f"Unknown action type: {action_type}")

    analysis = Analysis(
        document_id=document_id,
        action_type=action_type,
        summary_format=summary_format,
        user_goal=user_goal,
        result_markdown=result_markdown,
        key_takeaways_json=key_takeaways,
    )
    db.add(analysis)
    await db.flush()

    for cit in citations_data:
        db_cit = Citation(
            document_id=document_id,
            chunk_id=cit["chunk_id"],
            analysis_id=analysis.id,
            citation_label=cit["citation_label"],
            citation_type=cit["citation_type"],
            page_number=cit.get("page_number"),
            section_heading=cit.get("section_heading"),
            timestamp_formatted=cit.get("timestamp_formatted"),
            timestamp_seconds=cit.get("timestamp_seconds"),
            quote_text=cit["quote_text"],
        )
        db.add(db_cit)

    await db.commit()
    await db.refresh(analysis)
    return analysis, False
