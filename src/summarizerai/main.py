import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from summarizerai.config import settings
from summarizerai.database.session import init_db
from summarizerai.api.router import api_router

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database tables
    logger.info("Initializing SummarizerAI database...")
    await init_db()
    yield
    # Shutdown
    logger.info("SummarizerAI shutting down...")

app = FastAPI(
    title="SummarizerAI API",
    description="Local-first AI Content Intelligence Web Application for PDFs, Text, Websites, YouTube & Research Papers.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount central API router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handling request {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred.", "error": str(exc)},
    )

def main():
    import uvicorn
    uvicorn.run("summarizerai.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
