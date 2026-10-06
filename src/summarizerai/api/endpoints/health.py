from fastapi import APIRouter
from summarizerai.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def check_health():
    """
    Returns the current application health and active LLM provider info.

    Ollama status is shown only when Ollama is the configured default provider,
    so the app does not require Ollama to be running for normal Gemini operation.
    """
    provider = (getattr(settings, "LLM_PROVIDER", None) or settings.DEFAULT_LLM_PROVIDER or "gemini").lower()

    llm_info: dict = {
        "default_provider": provider,
        "active_model": None,
    }

    if provider == "gemini":
        llm_info["active_model"] = settings.GEMINI_MODEL
        llm_info["embedding_model"] = settings.GEMINI_EMBEDDING_MODEL
        llm_info["gemini_key_configured"] = bool(settings.GEMINI_API_KEY)

    elif provider == "ollama":
        from summarizerai.llm.ollama_provider import OllamaProvider
        ollama = OllamaProvider()
        ollama_online = await ollama.is_available()
        models = await ollama.list_models() if ollama_online else []
        llm_info["active_model"] = settings.OLLAMA_MODEL
        llm_info["ollama_online"] = ollama_online
        llm_info["ollama_models"] = models

    elif provider == "openai":
        llm_info["active_model"] = settings.OPENAI_MODEL
        llm_info["openai_key_configured"] = bool(settings.OPENAI_API_KEY)

    else:
        llm_info["active_model"] = "local_fallback"

    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "database": "connected",
        "llm": llm_info,
    }
