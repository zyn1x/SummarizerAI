from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from summarizerai.database.session import get_db
from summarizerai.models.document import Document
from summarizerai.models.chunk import Chunk
from summarizerai.schemas.document import DocumentResponse, DocumentDetailResponse
from summarizerai.schemas.chunk import ChunkResponse

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("", response_model=List[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    docs = list(result.scalars().all())
    
    # Enrich with chunk count
    response_list = []
    for doc in docs:
        count_res = await db.execute(
            select(func.count(Chunk.id)).where(Chunk.document_id == doc.id)
        )
        c_count = count_res.scalar() or 0
        doc_dict = {
            "id": doc.id,
            "title": doc.title,
            "source_type": doc.source_type,
            "source_url": doc.source_url,
            "original_filename": doc.original_filename,
            "file_size_bytes": doc.file_size_bytes,
            "summary_short": doc.summary_short,
            "metadata_json": doc.metadata_json,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
            "chunk_count": c_count,
        }
        response_list.append(DocumentResponse(**doc_dict))
    return response_list

@router.get("/{doc_id}", response_model=DocumentDetailResponse)
async def get_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.analyses))
        .where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    count_res = await db.execute(
        select(func.count(Chunk.id)).where(Chunk.document_id == doc.id)
    )
    c_count = count_res.scalar() or 0

    preview = doc.raw_text[:2000] if doc.raw_text else ""
    return DocumentDetailResponse(
        id=doc.id,
        title=doc.title,
        source_type=doc.source_type,
        source_url=doc.source_url,
        original_filename=doc.original_filename,
        file_size_bytes=doc.file_size_bytes,
        summary_short=doc.summary_short,
        metadata_json=doc.metadata_json,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        chunk_count=c_count,
        raw_text_preview=preview,
        has_analyses=len(doc.analyses) > 0,
        analyses_count=len(doc.analyses),
    )

@router.get("/{doc_id}/chunks", response_model=List[ChunkResponse])
async def get_document_chunks(doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Chunk).where(Chunk.document_id == doc_id).order_by(Chunk.chunk_index)
    )
    chunks = result.scalars().all()
    return chunks

@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    await db.delete(doc)
    await db.commit()
    return {"message": "Document deleted successfully."}
