from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from summarizerai.database.session import get_db
from summarizerai.models.analysis import Analysis
from summarizerai.schemas.analysis import (
    AnalysisRequest,
    ActionableInsightsRequest,
    AnalysisResponse,
    CitationResponse,
)
from summarizerai.services.document_service import get_or_create_analysis

router = APIRouter(prefix="/documents/{doc_id}/actions", tags=["Actions"])

def format_analysis_response(analysis: Analysis, is_cached: bool = False) -> AnalysisResponse:
    citations_data = [
        CitationResponse(
            id=c.id,
            citation_label=c.citation_label,
            citation_type=c.citation_type,
            page_number=c.page_number,
            section_heading=c.section_heading,
            timestamp_formatted=c.timestamp_formatted,
            timestamp_seconds=c.timestamp_seconds,
            quote_text=c.quote_text,
            chunk_id=c.chunk_id,
        )
        for c in (analysis.citations or [])
    ]

    return AnalysisResponse(
        id=analysis.id,
        document_id=analysis.document_id,
        action_type=analysis.action_type,
        summary_format=analysis.summary_format,
        user_goal=analysis.user_goal,
        result_markdown=analysis.result_markdown,
        key_takeaways=analysis.key_takeaways_json or [],
        citations=citations_data,
        created_at=analysis.created_at,
        is_cached=is_cached,
    )

@router.post("/summary", response_model=AnalysisResponse)
async def generate_summary_action(
    doc_id: str,
    payload: AnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        analysis, is_cached = await get_or_create_analysis(
            document_id=doc_id,
            action_type="summary",
            summary_format=payload.summary_format.value if payload.summary_format else "executive",
            user_goal=None,
            db=db,
            force_refresh=payload.force_refresh,
        )
        # Reload with citations
        res = await db.execute(
            select(Analysis).options(selectinload(Analysis.citations)).where(Analysis.id == analysis.id)
        )
        reloaded = res.scalar_one()
        return format_analysis_response(reloaded, is_cached)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/key_points", response_model=AnalysisResponse)
async def generate_key_points_action(
    doc_id: str,
    force_refresh: bool = False,
    db: AsyncSession = Depends(get_db)
):
    try:
        analysis, is_cached = await get_or_create_analysis(
            document_id=doc_id,
            action_type="key_points",
            summary_format=None,
            user_goal=None,
            db=db,
            force_refresh=force_refresh,
        )
        res = await db.execute(
            select(Analysis).options(selectinload(Analysis.citations)).where(Analysis.id == analysis.id)
        )
        reloaded = res.scalar_one()
        return format_analysis_response(reloaded, is_cached)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights", response_model=AnalysisResponse)
async def generate_actionable_insights_action(
    doc_id: str,
    payload: ActionableInsightsRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        analysis, is_cached = await get_or_create_analysis(
            document_id=doc_id,
            action_type="actionable_insights",
            summary_format=None,
            user_goal=payload.user_goal.value,
            db=db,
            force_refresh=payload.force_refresh,
        )
        res = await db.execute(
            select(Analysis).options(selectinload(Analysis.citations)).where(Analysis.id == analysis.id)
        )
        reloaded = res.scalar_one()
        return format_analysis_response(reloaded, is_cached)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[AnalysisResponse])
async def list_document_analyses(doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Analysis)
        .options(selectinload(Analysis.citations))
        .where(Analysis.document_id == doc_id)
        .order_by(Analysis.created_at.desc())
    )
    analyses = result.scalars().all()
    return [format_analysis_response(a, is_cached=True) for a in analyses]
