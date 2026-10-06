import os
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from summarizerai.database.session import get_db, async_session_factory
from summarizerai.models.job import ProcessingJob
from summarizerai.schemas.document import IngestUrlRequest, IngestResponse
from summarizerai.ingestion.security import sanitize_filename, validate_file, validate_ssrf_safe_url
from summarizerai.ingestion.detector import detect_file_source_type, detect_url_source_type
from summarizerai.ingestion.pdf_extractor import extract_pdf_content
from summarizerai.ingestion.txt_extractor import extract_txt_content
from summarizerai.ingestion.web_extractor import extract_web_content
from summarizerai.ingestion.youtube_extractor import extract_youtube_content
from summarizerai.ingestion.research_extractor import extract_research_paper
from summarizerai.services.document_service import create_document_from_canonical
from summarizerai.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["Ingestion"])

async def process_file_background(job_id: str, file_path: str, filename: str, source_type: str):
    """Background pipeline for file ingestion."""
    async with async_session_factory() as db:
        try:
            job = await db.get(ProcessingJob, job_id)
            if not job:
                return

            job.status = "extracting"
            job.progress_percent = 25
            job.current_step = f"Extracting content from {source_type.upper()} file..."
            await db.commit()

            if source_type == "pdf":
                canon_doc = extract_pdf_content(file_path, filename)
            else:
                canon_doc = extract_txt_content(file_path, filename)

            job.status = "normalizing"
            job.progress_percent = 45
            job.current_step = "Normalizing content and detecting document structure..."
            await db.commit()

            await create_document_from_canonical(canon_doc, db, job_id=job_id)

        except Exception as e:
            logger.error(f"Error in background file processing: {e}", exc_info=True)
            job = await db.get(ProcessingJob, job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.current_step = f"Failed: {str(e)}"
                await db.commit()
        finally:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

async def process_url_background(job_id: str, url: str, source_type: str):
    """Background pipeline for URL ingestion (web, youtube, research paper)."""
    async with async_session_factory() as db:
        try:
            job = await db.get(ProcessingJob, job_id)
            if not job:
                return

            job.status = "extracting"
            job.progress_percent = 25
            job.current_step = f"Fetching and extracting from {source_type.replace('_', ' ').title()}..."
            await db.commit()

            if source_type == "youtube":
                canon_doc = await extract_youtube_content(url)
            elif source_type == "research_paper":
                canon_doc = await extract_research_paper(url)
            else:
                canon_doc = await extract_web_content(url)

            job.status = "normalizing"
            job.progress_percent = 45
            job.current_step = "Normalizing content and chunking..."
            await db.commit()

            await create_document_from_canonical(canon_doc, db, job_id=job_id)

        except Exception as e:
            logger.error(f"Error in background URL processing: {e}", exc_info=True)
            job = await db.get(ProcessingJob, job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.current_step = f"Failed: {str(e)}"
                await db.commit()

@router.post("/file", response_model=IngestResponse)
async def ingest_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process PDF or TXT document."""
    clean_name = sanitize_filename(file.filename or "uploaded_doc")
    
    # Read bytes to validate size
    content = await file.read()
    validate_file(clean_name, len(content))

    source_type = detect_file_source_type(clean_name)
    temp_path = settings.TEMP_DIR / f"{uuid.uuid4()}_{clean_name}"
    
    with open(temp_path, "wb") as f:
        f.write(content)

    temp_doc_id = str(uuid.uuid4())
    job = ProcessingJob(
        document_id=temp_doc_id,
        status="uploading",
        progress_percent=10,
        current_step="File uploaded successfully. Initializing ingestion..."
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Launch background task
    background_tasks.add_task(
        process_file_background,
        job_id=job.id,
        file_path=str(temp_path),
        filename=clean_name,
        source_type=source_type
    )

    return IngestResponse(
        document_id=temp_doc_id,
        job_id=job.id,
        status="processing",
        message="File received and queued for ingestion."
    )

@router.post("/url", response_model=IngestResponse)
async def ingest_url(
    payload: IngestUrlRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Ingest website, YouTube video, or research paper URL."""
    clean_url = validate_ssrf_safe_url(payload.url)
    source_type = detect_url_source_type(clean_url)

    temp_doc_id = str(uuid.uuid4())
    job = ProcessingJob(
        document_id=temp_doc_id,
        status="uploading",
        progress_percent=10,
        current_step=f"Validating {source_type.replace('_', ' ').title()} source..."
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(
        process_url_background,
        job_id=job.id,
        url=clean_url,
        source_type=source_type
    )

    return IngestResponse(
        document_id=temp_doc_id,
        job_id=job.id,
        status="processing",
        message=f"{source_type.title()} URL queued for extraction."
    )
