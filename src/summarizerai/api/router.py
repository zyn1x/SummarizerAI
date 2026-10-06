from fastapi import APIRouter
from summarizerai.api.endpoints.health import router as health_router
from summarizerai.api.endpoints.ingest import router as ingest_router
from summarizerai.api.endpoints.jobs import router as jobs_router
from summarizerai.api.endpoints.documents import router as documents_router
from summarizerai.api.endpoints.actions import router as actions_router
from summarizerai.api.endpoints.qa import router as qa_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(ingest_router)
api_router.include_router(jobs_router)
api_router.include_router(documents_router)
api_router.include_router(actions_router)
api_router.include_router(qa_router)
