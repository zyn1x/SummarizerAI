import numpy as np
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from summarizerai.models.document import Document
from summarizerai.models.chunk import Chunk
from summarizerai.models.qa import QAInteraction
from summarizerai.llm.provider import LLMProvider
from summarizerai.schemas.qa import CitationItem

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    a = np.array(v1, dtype=float)
    b = np.array(v2, dtype=float)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

async def answer_question(
    document_id: str,
    question: str,
    db: AsyncSession,
    llm: LLMProvider,
    top_k: int = 5
) -> Tuple[str, bool, List[CitationItem], QAInteraction]:
    """
    RAG service:
    1. Embeds question.
    2. Performs vector similarity search across document chunks.
    3. Synthesizes grounded answer.
    4. Cites source evidence.
    5. Flags when source material is insufficient.
    """
    # Fetch document
    doc_res = await db.execute(select(Document).where(Document.id == document_id))
    doc = doc_res.scalar_one_or_none()
    if not doc:
        raise ValueError(f"Document {document_id} not found.")

    # Fetch chunks
    chunks_res = await db.execute(select(Chunk).where(Chunk.document_id == document_id).order_by(Chunk.chunk_index))
    chunks = list(chunks_res.scalars().all())
    if not chunks:
        # pyrefly: ignore [bad-return]
        return "This document has no readable text chunks.", False, [], None

    # Embed question
    q_embeddings = await llm.embed([question])
    q_vec = q_embeddings[0] if q_embeddings else [0.0] * 256

    # Score chunks
    scored_chunks: List[Tuple[float, Chunk]] = []
    
    # Check if chunks have embeddings; if not, embed on the fly
    missing_embed_chunks = [c for c in chunks if not c.embedding_json]
    if missing_embed_chunks:
        texts_to_embed = [c.content for c in missing_embed_chunks]
        new_embeddings = await llm.embed(texts_to_embed)
        for c, emb in zip(missing_embed_chunks, new_embeddings):
            c.embedding_json = emb
        await db.commit()

    q_words = set(question.lower().split())

    for chunk in chunks:
        sim = 0.0
        if chunk.embedding_json:
            sim = cosine_similarity(q_vec, chunk.embedding_json)
        
        # Word overlap boost
        chunk_words = set(chunk.content.lower().split())
        overlap = len(q_words & chunk_words) / (len(q_words) + 1e-5)
        hybrid_score = 0.7 * sim + 0.3 * overlap

        scored_chunks.append((hybrid_score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_scored = scored_chunks[:top_k]
    top_chunks = [c for _, c in top_scored]
    highest_score = top_scored[0][0] if top_scored else 0.0

    # Build context
    context_blocks = []
    citation_items: List[CitationItem] = []

    for _, c in top_scored:
        if c.page_number is not None:
            label = f"[p. {c.page_number}]"
            c_type = "page"
        elif c.timestamp_formatted:
            label = f"[{c.timestamp_formatted}]"
            c_type = "timestamp"
        elif c.section_heading:
            clean_head = c.section_heading.strip()
            if len(clean_head) > 20:
                clean_head = clean_head[:17] + "..."
            label = f"[{clean_head}]"
            c_type = "section"
        else:
            label = f"[Chunk {c.chunk_index + 1}]"
            c_type = "chunk"

        context_blocks.append(f"{label} {c.content}")
        
        # Extract quote
        preview_quote = c.content[:160].strip()
        if len(c.content) > 160:
            preview_quote += "..."

        citation_items.append(
            CitationItem(
                chunk_id=c.id,
                citation_label=label,
                citation_type=c_type,
                page_number=c.page_number,
                section_heading=c.section_heading,
                timestamp_formatted=c.timestamp_formatted,
                timestamp_seconds=c.timestamp_start,
                quote_text=preview_quote
            )
        )

    context_str = "\n\n".join(context_blocks)

    system_prompt = """You are SummarizerAI's grounded Q&A engine.
Answer the user's question using ONLY the provided Source Excerpts.
CRITICAL RULES:
1. If the excerpts DO NOT contain sufficient information to answer the question, explicitly state:
"The provided source document does not contain enough information to answer this question."
Do not make assumptions or invent facts outside the text.
2. When answering, cite the excerpt markers like [p. 2], [04:15], or [Section Name] next to specific claims.
3. Keep your answers direct, structured, and informative."""

    prompt = f"""Source Excerpts:
{context_str}

User Question:
{question}
"""

    answer = await llm.generate(prompt, system_prompt=system_prompt)
    is_grounded = "does not contain enough information" not in answer.lower()

    # Save interaction to DB
    qa_record = QAInteraction(
        document_id=document_id,
        question=question,
        answer=answer,
        is_grounded=is_grounded,
        citations_json=[cit.model_dump() for cit in citation_items],
        retrieved_chunk_ids=[c.id for c in top_chunks]
    )
    db.add(qa_record)
    await db.commit()
    await db.refresh(qa_record)

    return answer, is_grounded, citation_items, qa_record
