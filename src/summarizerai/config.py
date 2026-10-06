import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "SummarizerAI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # ------------------------------------------------------------------ #
    # Persistence – SQLite for local dev; PostgreSQL + pgvector in prod   #
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = "sqlite+aiosqlite:///./summarizer.db"

    # ------------------------------------------------------------------ #
    # LLM Provider Selection                                               #
    #   Supported: "gemini" (default), "ollama", "openai", "fallback"     #
    # ------------------------------------------------------------------ #
    LLM_PROVIDER: str = "gemini"
    DEFAULT_LLM_PROVIDER: str = "gemini"

    # -- Google Gemini (primary cloud provider) -------------------------  #
    # Keys are loaded from .env and NEVER sent to the frontend.
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-2"

    # -- Ollama (optional local provider, zero mandatory dependency) ----- #
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"

    # -- Optional additional cloud providers ----------------------------- #
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    HUGGINGFACE_API_KEY: str = ""

    # ------------------------------------------------------------------ #
    # Storage & upload limits                                              #
    # ------------------------------------------------------------------ #
    UPLOAD_DIR: Path = Path("./data/uploads")
    TEMP_DIR: Path = Path("./data/temp")
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt", ".md"]

    # ------------------------------------------------------------------ #
    # Security & SSRF guard                                               #
    # ------------------------------------------------------------------ #
    ALLOWED_SCHEMES: List[str] = ["http", "https"]
    REQUEST_TIMEOUT_SECONDS: int = 30
    MAX_CHUNKS_PER_DOC: int = 1500


settings = Settings()

# Ensure upload/temp directories exist on startup
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
