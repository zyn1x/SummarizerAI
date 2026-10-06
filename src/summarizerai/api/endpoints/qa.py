from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from summarizerai.database.session import get_db
from summarizerai.models.qa import QAInteraction
from summarizerai.schemas.qa import QARequest, QAResponse, QAHistoryItem
from summarizerai.services.rag_service import answer_question
from summarizerai.llm.factory import get_llm_provider

router = APIRouter(prefix="/documents/{doc_id}/qa", tags=["Q&A"])

@router.post("", response_model=QAResponse)
async def ask_question_endpoint(
    doc_id: str,
    payload: QARequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        llm = await get_llm_provider()
        answer, is_grounded, citations, qa_record = await answer_question(
            document_id=doc_id,
            question=payload.question,
            db=db,
            llm=llm,
            top_k=payload.top_k,
        )

        return QAResponse(
            id=qa_record.id,
            document_id=doc_id,
            question=payload.question,
            answer=answer,
            is_grounded=is_grounded,
            citations=citations,
            created_at=qa_record.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[QAHistoryItem])
async def get_qa_history(doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(QAInteraction)
        .where(QAInteraction.document_id == doc_id)
        .order_by(QAInteraction.created_at.asc())
    )
    items = result.scalars().all()
    return items
